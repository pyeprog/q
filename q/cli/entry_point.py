import asyncio
from contextlib import suppress
from dataclasses import fields
from itertools import chain
import json
from pathlib import Path
import subprocess
import sys

from pydantic_ai.messages import (
    BaseToolCallPart,
    BaseToolReturnPart,
    FilePart,
    RetryPromptPart,
    TextPart,
    ThinkingPart,
    UserPromptPart,
)
from pydantic_graph.persistence.file import FileStatePersistence
from pydantic_graph.persistence import Snapshot
from rich.table import Table
import toml
from q.cli.manager import GlobalToolMap
from q.workflow.repository import WORKFLOW_MAP
from q.workflow.persistence import PERSISTENCE_FILENAME
from q.workflow.util.config import LocalConfigLoader, WorkflowConfig
from q.workflow.agent.internal_tool import InternalToolMap
from q.workflow.util.config import load_config, save_config
from q.workflow.util.deps import BaseDeps
from q.cli.config import centralized_config
from q.cli.manager.module.workflow import workflow_manager
from q.cli.manager.module.tool import tool_manager
from q.workflow.util.node import ConfigurableNode
from q.cli.console import CliConsole, panel_param_by_content, console
from q.workflow.util.output import ExtraParam
from q.cli.manager.mcp import SSEMCP, StdioMCP, StreamableHttpMCP, mcp_manager


def query(user_input: str, extra_tool_names: list[str], plain: bool = False, working_dir: str | Path = "."):
    """start querying with AI agent

    Args:
        user_input (str): user's prompt
        extra_tool_names (list[str]): extra function tool names
        plain (bool): whether to print plain text without rich formatting
        working_dir (str | Path): working directory containing config and history
    """
    assert user_input, "user_input should not be empty"

    workflow_config = load_config(working_dir)
    workflow_name = workflow_config.workflow_name

    workflow_cls = workflow_manager.workflow_map.get(workflow_name, None)

    if not workflow_cls:
        print(
            f"Workflow {workflow_name} not found, use workflow command to check them out",
            file=sys.stderr,
        )
        exit(1)

    workflow = workflow_cls(
        deps=BaseDeps(
            tool_map=GlobalToolMap,
            extra_tool_names=extra_tool_names,
            console=CliConsole(plain),
            gen_agent_extra_param=lambda title: ExtraParam(panel_param_by_content(title)),
            working_dir=working_dir,
        ),
    )
    workflow.entry(user_input)


def create_query(directory: str | Path, workflow: str, extra_tool_names: list[str], refer_dir: str | Path | None = None):
    """create necessary config file for query in given directory

    Args:
        directory (str | Path): target directory
        workflow (str): workflow name, corresponding to keys in WORKFLOW_MAP
        extra_tool_names (list[str]): extra function tool names
        refer_dir (str): referenced directory(other query directory), which is used when you want to refer its message history
    """
    # create directory if it's not existed
    path = Path(directory)
    if path.is_file():
        print(
            f"Path {str(path)!r} is a file, please provide a directory path.",
            file=sys.stderr,
        )
        exit(1)

    path.mkdir(parents=True, exist_ok=True)

    # generate .env file to this path
    centralized_config.to_env_file(path / ".env")

    # generate agent_config.json file to this path
    # how to do it:
    # 1. iterate through each node inheritted from NodeFileConfig
    # 2. get agent_config_dict from each one of them
    # 3. merge them into one agent_config_dict and
    # 4. save it to agent_config.json file under given path
    workflow_map = workflow_manager.workflow_map
    workflow_cls = workflow_map.get(workflow, None)

    if not workflow_cls:
        print(f"Workflow {workflow} not found, use workflow command to check them out", file=sys.stderr)
        exit(1)

    workflow_graph = workflow_cls.graph()
    workflow_config = WorkflowConfig(workflow_name=workflow)
    for node_def in workflow_graph.node_defs.values():
        if issubclass(node_def.node, ConfigurableNode):
            agent_config = node_def.node.agent_config()

            # add extra tool names into agent config of each node
            for config in agent_config.values():
                config.tool_names.update(extra_tool_names)

            # workflow_config collects agent_config or each nodes
            workflow_config.agent_config_map.update(agent_config)

    save_config(config=workflow_config, dir_=path)

    if not refer_dir:
        return

    # create history.json from other query's history.json if refer is specified
    async def _helper():
        ref_path = Path(refer_dir)
        if not (ref_path.is_dir() and (ref_path / "history.json").is_file()):
            print(f"Path {refer_dir} is not valid query", file=sys.stderr)
            exit(1)

        loader = LocalConfigLoader(ref_path, workflow_map)
        translation_config = {
            "src": {"available_fields": [f.name for f in fields(loader.state_type)]},  # type: ignore
            "dst": {f.name: [] for f in fields(workflow_graph._state_type)},  # type: ignore
            "starting_node": {
                "description": f"available node {workflow_graph.node_defs.keys()}, specify its fields for initializing if needed",
                "node_id": "choose node in description",
            },
        }

        # create a temporary file to edit
        temporary_filename = ".state_translation.toml"
        with open(temporary_filename, "w") as fp:
            toml.dump(translation_config, fp)

        try:
            editor_cmd = centralized_config.config.get("EDITOR", "vim")
            subprocess.run([editor_cmd, temporary_filename], check=True)
        except Exception as e:
            print(f"An unexpected error occurred while invoking editor: {e}", file=sys.stderr)
            exit(1)

        # make a temporary file for further edit
        with open(temporary_filename, "r") as fp:
            modified_translation_config = toml.load(fp)

        # generate a node as the next node and save it in the snapshot
        node_def = workflow_graph.node_defs[modified_translation_config["starting_node"]["node_id"]].node
        node_params = {f.name for f in fields(node_def)}  # type: ignore
        given_node_params = {k: v for k, v in modified_translation_config["starting_node"].items() if k in node_params}
        node = node_def(**given_node_params)

        # generate a state according to reference state and translation rule in the config
        snapshots = await loader.snapshots()
        if not snapshots:
            print(f"No snapshots found in refer directory {refer_dir}", file=sys.stderr)
            exit(1)

        src_state = snapshots[-1].state
        dst_state_fields = {}
        for dst_field_name, src_field_names in modified_translation_config["dst"].items():
            dst_state_fields[dst_field_name] = list(
                chain.from_iterable([getattr(src_state, name) for name in src_field_names])
            )
        state = workflow_graph._state_type(**dst_state_fields)  # type: ignore

        # save snapshot into history.json as the initial history
        persistence = FileStatePersistence(path / PERSISTENCE_FILENAME)
        persistence.set_graph_types(workflow_graph)
        await persistence.snapshot_node(state=state, next_node=node)

        # delete temporary file
        Path(temporary_filename).unlink(missing_ok=True)

    asyncio.run(_helper())


def info(directory: str | Path):
    """show info about number of snapshots and state's available fields in each snapshot. Notice that snapshot is the running step of workflow,
      which contains workflow state of corresponding step.

    Args:
        directory (str): specified directory
    """

    async def _helper():
        loader = LocalConfigLoader(directory, workflow_manager.workflow_map)
        console.print(
            ",".join([field.name for field in fields(loader.state_type)]),  # type: ignore
            extra_param=ExtraParam(panel_param_by_content("Available Fields")),
        )

        if snapshots := await loader.snapshots():
            console.print(f"[0-{len(snapshots) - 1}]", extra_param=ExtraParam(panel_param_by_content("Snapshot Index")))

    asyncio.run(_helper())


def ls(directory: str | Path, snapshot: int, field: str):
    """list query messages

    Args:
        directory (str): specified directory
        snapshot (str): the index of snapshot
        field (str): the field of state
    """

    async def _helper():
        loader = LocalConfigLoader(directory, workflow_manager.workflow_map)

        index = snapshot
        snapshots = await loader.snapshots()
        snapshot_obj: Snapshot = snapshots[index]
        state = snapshot_obj.state

        chosen_field: str = field
        if not field:  # the field is empty, choose the first field retrieved
            all_fields = fields(state)
            chosen_field = all_fields[0].name

        for msg in getattr(state, chosen_field):
            for part in getattr(msg, "parts", []):
                if isinstance(part, UserPromptPart):
                    console.print(part.content, extra_param=ExtraParam(panel_param_by_content(part.part_kind)))

                elif isinstance(part, BaseToolCallPart):
                    lines: list[str] = []
                    for key, value in part.args_as_dict().items():
                        if hasattr(value, "__str__"):  # value is printable
                            lines.append(f"# {key}")
                            lines.append(value)

                    content = "\n".join(lines)
                    console.print(
                        content, extra_param=ExtraParam(panel_param_by_content(getattr(part, "part_kind", "tool-call")))
                    )

                elif isinstance(part, BaseToolReturnPart):
                    console.print(
                        part.content,
                        extra_param=ExtraParam(panel_param_by_content(getattr(part, "part_kind", "tool-return"))),
                    )

                elif isinstance(part, (RetryPromptPart, TextPart, ThinkingPart)):
                    console.print(part.content, extra_param=ExtraParam(panel_param_by_content(part.part_kind)))

                elif isinstance(part, FilePart):
                    content = f"{part.id} from {part.provider_name}"
                    console.print(content, extra_param=ExtraParam(panel_param_by_content(part.part_kind)))

    asyncio.run(_helper())


def print_config():
    """print all config key-value pairs stored in centralized config file"""
    console.print(str(centralized_config.file_path), extra_param=ExtraParam(panel_param_by_content("Config file")))

    key_values = "\n".join([f"- {key} = {value}" for key, value in centralized_config.config.items()])
    console.print(key_values, extra_param=ExtraParam(panel_param_by_content("Content")))


def set_config(key_value_strs: list[str]):
    """save given config to config file

    Args:
        key_value_strs (list[str]): config strings with each in format of `<key>=<value>`. This is the format returned by argparse
    """
    config_dict: dict[str, str] = {}
    for key_value_str in key_value_strs:
        try:
            key, value = key_value_str.split("=")
            key = key.strip()
            value = value.strip()
            config_dict[key] = value
        except Exception:
            print("Invalid key=value pair: {key_value_str}, please check your input", file=sys.stderr)

    centralized_config.set(config_dict)


def unset_config(keys: list[str]):
    """remove keys from config file

    Args:
        keys (list[str]): keys in format of [<key1>, <key2>, ...]
    """
    centralized_config.unset(keys)


def print_workflows():
    """print all workflows"""
    table = Table()
    table.add_column("Workflow", style="cyan")
    table.add_column("Module", style="magenta")
    table.add_column("Deletable", style="green", justify="right")

    for module in workflow_manager.modules:
        for cls in module.workflow_classes:
            table.add_row(cls.__name__, module.mod_name, "True")

    for name in WORKFLOW_MAP.keys():
        table.add_row(name, "Internal", "False")

    console.print(table)


def rm_workflow_mod(workflow_mod_names: list[str]):
    """remove workflow modules by given module names, invalid name will be ignored

    Args:
        workflow_mod_names (list[str]): list of module names
    """
    workflow_manager.rm_modules(workflow_mod_names)


def add_workflow_mod(workflow_mod_paths: list[str | Path]):
    """add workflow modules by given paths(either python file path or python module directory path)

    Args:
        workflow_mod_paths (list[str  |  Path]): module paths
    """
    workflow_manager.add_modules(workflow_mod_paths)


def print_tools():
    """print all tools"""
    table = Table(title="Function Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Module", style="magenta")
    table.add_column("Deletable", style="green", justify="right")
    for module in tool_manager.modules:
        for tool in module.tool_functions:
            table.add_row(tool.__name__, module.mod_name, "True")

    for name in InternalToolMap.dict.keys():
        table.add_row(name, "Internal", "False")

    console.print(table)

    table = Table(title="MCP Tools")
    table.add_column("MCP Tool", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Deletable", style="green", justify="right")

    for name, mcp in mcp_manager.mcp_map.items():
        if isinstance(mcp, StreamableHttpMCP):
            type_ = "Streamable Http"
        elif isinstance(mcp, SSEMCP):
            type_ = "SSE"
        elif isinstance(mcp, StdioMCP):
            type_ = "Stdio"
        else:
            type_ = "Unknown"
        table.add_row(name, type_, "True")

    console.print(table)


def rm_tool_mod(tool_mod_names: list[str]):
    """remove tool modules by given module names, invalid name will be ignored

    Args:
        tool_mod_names (list[str]): list of module names
    """
    tool_manager.rm_modules(tool_mod_names)
    mcp_manager.rm_all(tool_mod_names)


def add_tool_mod(list_of_mod_path_or_json: list[str | Path]):
    """add tool modules by given paths(either python file path or python module directory path)

    Args:
        tool_mod_paths (list[str  |  Path]): module paths
    """

    def is_json(mod_path_or_json):
        with suppress(Exception):
            json.loads(mod_path_or_json)
            return True

        return False

    for mod_path_or_json in list_of_mod_path_or_json:
        if is_json(mod_path_or_json):
            config_json = mod_path_or_json
            mcp_manager.add_config_json(config_json)
        else:
            tool_manager.add_modules([mod_path_or_json])
