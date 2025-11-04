import argparse
from pathlib import Path


def parser():
    _parser = argparse.ArgumentParser(prog="query", description="a cli for AI agent or workflow")

    subcommand = _parser.add_subparsers(title="subcommand", dest="command")

    say_parser = subcommand.add_parser(
        "say",
        aliases=["s"],
        help="chat with agent or workflow",
        description="chat with agent or workflow, but make sure cd to query directory first",
    )
    say_parser.add_argument("prompt", type=str, default="", nargs="?", help="user prompt given to AI agent or workflow")
    # TODO: extra_tools show no full tool list in help info
    say_parser.add_argument(
        "--extra_tools",
        "-t",
        type=str,
        default=[],
        action="extend",
        nargs="*",
        dest="extra_tools",
        help="extra function tools for AI agent",
        metavar="check out using tool subcommand",
    )

    create_parser = subcommand.add_parser(
        "create",
        aliases=["c"],
        help="create a query directory",
        description="create a directory and init config file in it",
    )
    create_parser.add_argument(
        "directory",
        type=Path,
        default=Path.cwd(),
        nargs="?",
        help="target directory, default is current working directory",
    )
    create_parser.add_argument(
        "--workflow",
        "-w",
        type=str,
        default="default",
        nargs="?",
        dest="workflow",
        help="specify which workflow to init the directory",
        metavar="check out using workflow subcommand",
    )
    create_parser.add_argument(
        "--refer_dir",
        "-r",
        type=Path,
        default=None,
        nargs="?",
        dest="refer_dir",
        help="specify which qiery directory to refer to",
    )

    info_parser = subcommand.add_parser("info", help="list meta info about the query")
    info_parser.add_argument(
        "directory", type=Path, default=Path.cwd(), nargs="?", help="the path of (query) directory, default as $(pwd)"
    )

    ls_parser = subcommand.add_parser(
        "ls", help="list the query message of directory I'm staying in. the structure: snapshots[n].state.[field]"
    )
    ls_parser.add_argument(
        "directory", type=Path, default=Path.cwd(), nargs="?", help="the path of (query) directory, default as $(pwd)"
    )
    ls_parser.add_argument(
        "--snapshot",
        "-s",
        type=int,
        default=-1,
        nargs="?",
        dest="snapshot",
        help="the index of snapshot, use info to see the range",
    )
    ls_parser.add_argument(
        "--field",
        "-f",
        type=str,
        default="",
        nargs="?",
        dest="field",
        help="the field of the state, default to use the `first` field",
    )

    config_parser = subcommand.add_parser("config", help="config platform keys, default model, and more")
    config_parser.add_argument(
        "--set", action="extend", nargs="+", type=str, dest="key_value_strs", help="key=value pairs to set in config"
    )
    config_parser.add_argument(
        "--unset", action="extend", nargs="+", type=str, dest="unset_keys", help="keys to unset from config"
    )

    workflow_parser = subcommand.add_parser("workflow", aliases=["w"], help="add, remove, list workflows")
    workflow_parser.add_argument(
        "--add",
        action="extend",
        nargs="+",
        type=Path,
        dest="workflow_mods_to_add",
        help="paths of workflow module to add, a single module might have multiple workflows",
        metavar="python_mod_path"
    )
    workflow_parser.add_argument(
        "--rm",
        action="extend",
        nargs="+",
        type=str,
        dest="workflow_mods_to_rm",
        help="names of workflow module to remove, a single module might have multiple workflows",
        metavar="workflow_module_name"
    )

    return _parser
