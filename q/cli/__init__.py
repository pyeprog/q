import sys
from q.cli.entry_point import (
    add_tool_mod,
    add_workflow_mod,
    create_query,
    info,
    ls,
    print_config,
    print_tools,
    print_workflows,
    query,
    rm_tool_mod,
    rm_workflow_mod,
    set_config,
    unset_config,
)
from q.cli.parser import parser


def main():
    _parser = parser()
    args = _parser.parse_args()

    match args.command:
        case "say" | "s":
            if not args.prompt:
                print("prompt query should not be empty", file=sys.stderr)
                exit(1)

            query(user_input=args.prompt, extra_tools=args.extra_tools, plain=args.plain)

        case "create" | "c":
            create_query(directory=args.directory, workflow=args.workflow, refer_dir=args.refer_dir)

        case "info":
            info(directory=args.directory)

        case "ls":
            ls(directory=args.directory, snapshot=args.snapshot, field=args.field)

        case "config":
            if args.key_value_strs:
                set_config(key_value_strs=args.key_value_strs)

            elif args.unset_keys:
                unset_config(keys=args.unset_keys)

            else:
                print_config()

        case "workflow" | "w":
            if args.workflow_mods_to_add:
                add_workflow_mod(args.workflow_mods_to_add)

            elif args.workflow_mods_to_rm:
                rm_workflow_mod(args.workflow_mods_to_rm)

            else:
                print_workflows()

        case "tool" | "t":
            if args.tool_mods_to_add:
                add_tool_mod(args.tool_mods_to_add)

            elif args.tool_mods_to_rm:
                rm_tool_mod(args.tool_mods_to_rm)

            else:
                print_tools()

        case _:
            _parser.parse_args(["--help"])
