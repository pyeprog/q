import asyncio
from dataclasses import fields
from itertools import chain
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable

from pydantic_graph.persistence.file import FileStatePersistence
from pydantic_graph.persistence import Snapshot
import toml
from q.workflow import WORKFLOW_MAP
from q.workflow.persistence import PERSISTENCE_FILENAME
from q.workflow.util.config import LocalConfigLoader, WorkflowConfig
from q.workflow.agent.tool import tool_of
from q.workflow.util.config import ConfigurableNode, load_config, save_config
from q.workflow.util.deps import BaseDeps
from q.cli.config import centralized_config


def query(user_input: str, extra_tools: list[str] | None = None):
    """start querying with AI agent

    Args:
        user_input (str): user's prompt
        extra_tool (list[str]): extra function tools
    """
    workflow_config = load_config()
    workflow_cls = WORKFLOW_MAP.get(workflow_config.workflow_name)
    if not workflow_cls:
        print(f"Workflow {workflow_config.workflow_name} not found", file=sys.stderr)
        exit(1)

    extra_tools = extra_tools or []
    tools: list[Callable] = [tool_of(t) for t in extra_tools]

    workflow = workflow_cls(BaseDeps(tools))
    workflow.entry(user_input)


def create_query(directory: str | Path, workflow: str, refer_dir: str | Path | None = None):
    """create necessary config file for query in given directory

    Args:
        directory (str | Path): target directory
        workflow (str): workflow name, corresponding to keys in WORKFLOW_MAP
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
    workflow_cls = WORKFLOW_MAP.get(workflow, None)
    if not workflow_cls:
        print(
            f"Workflow {workflow!r} is not registered, available workflow: {list(WORKFLOW_MAP.keys())}", file=sys.stderr
        )
        exit(1)

    workflow_graph = workflow_cls(BaseDeps()).graph()
    workflow_config = WorkflowConfig(workflow_name=workflow)
    for node_def in workflow_graph.node_defs.values():
        if issubclass(node_def.node, ConfigurableNode):
            workflow_config.agent_config_map.update(node_def.node.agent_config())

    save_config(config=workflow_config, dir_=path)

    if not refer_dir:
        return

    # create history.json from other query's history.json if refer is specified
    async def _helper():
        ref_path = Path(refer_dir)
        if not (ref_path.is_dir() and (ref_path / "history.json").is_file()):
            print(f"Path {refer_dir} is not valid query", file=sys.stderr)
            exit(1)

        loader = LocalConfigLoader(ref_path)
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
            subprocess.run(["nvim", temporary_filename], check=True)
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
        loader = LocalConfigLoader(directory)
        print("these fields are supported: ", " | ".join([field.name for field in fields(loader.state_type)]))  # type: ignore

        if snapshots := await loader.snapshots():
            print(
                f"there are {len(snapshots)} versions of snapshot, index `[0-{len(snapshots) - 1}]`"
                "or `latest` to retrive the last one, if not given, the default will be latest"
            )

    asyncio.run(_helper())


def ls(directory: str | Path, snapshot: int, field: str):
    """list query messages

    Args:
        directory (str): specified directory
        snapshot (str): the index of snapshot
        field (str): the field of state
    """

    async def _helper():
        loader = LocalConfigLoader(directory)

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
                if hasattr(part, "content"):
                    print(part.content)

    asyncio.run(_helper())

    

def print_config():
    """print all config key-value pairs stored in centralized config file
    """
    print(f"[config file is at {str(centralized_config.file_path)}]", end='\n'*2)
    for key, value in centralized_config.config.items():
        print(f"{key} = {value}")

    
def set_config(key_value_strs: list[str]):
    """save given config to config file

    Args:
        key_value_strs (list[str]): config strings with each in format of `<key>=<value>`. This is the format returned by argparse
    """
    config_dict: dict[str, str] = {}
    for key_value_str in key_value_strs:
        try:
            key, value = key_value_str.split('=')
            key = key.strip()
            value = value.strip()
            config_dict[key] = value
        except:
            print("Invalid key=value pair: {key_value_str}, please check your input", file=sys.stderr)
            
    centralized_config.set(config_dict)


def unset_config(keys: list[str]):
    """remove keys from config file

    Args:
        keys (list[str]): keys in format of [<key1>, <key2>, ...]
    """
    centralized_config.unset(keys)