from q.cli.entry_point import create_query, info, ls, print_config, query, set_config, unset_config
from q.cli.parser import parser


def main():
    _parser = parser()
    args = _parser.parse_args()

    match args.command:
        case "say" | "s":
            query(user_input=args.prompt, extra_tools=args.extra_tools)

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

        case _:
            print("Unknown command")
            exit(1)
