# Q

"q" means query, which is a cli for agent application, including simple chatting, workflow, agentic action and more.

## Features

1. q can register tools and work with them.
2. q can register workflows and work with them.
3. there're many tools and workflows you can choose from.
4. local directory as chat cache, you can config model, tools, workflow, even edit message history with chat cache.


## How To

The CLI program is `q`. Available subcommands and their aliases:

- `say` (`s`): chat with an agent or workflow
- `create` (`c`): create and initialize a query directory
- `info`: show meta info about a query directory
- `ls`: list messages stored in a query directory
- `config`: set/unset configuration keys
- `workflow` (`w`): add/remove/list workflows
- `tool` (`t`): add/remove/list function tools

Examples and common usage:

- Create a query directory (default workflow is `default`):

	```bash
	q create <path> --workflow default
	# or using the alias
	q c <path> -w default
	```

	- `--refer_dir` / `-r` : copy settings from an existing query directory
	- `--extra_tools` / `-t` : comma-separated function tool names to register

- Create from another query directory:

	```bash
	q c <path> --w research -r /path/to/other/query
	```

- Chat with the agent/workflow (run inside the query directory):

	```bash
	cd <query-dir>
	q say "who are you?"
	# alias
	q s "who are you?"
	```

	Options:
	- `--extra_tools` / `-t` : specify extra tools as a comma-separated list (e.g. `toolA,toolB`)
	- `--plain` / `-p` : print plain text without rich formatting

- Inspect a query directory:

	```bash
	q info [directory]
	# default is the current directory when not provided
	```

- List stored messages and snapshots:

	```bash
	q ls [directory] [--snapshot N|latest] [--field name]
	# examples
	q ls
	q ls --snapshot 3
	q ls --snapshot latest --field first
	```

- Config management:

	```bash
	q config --set key1=value1 key2=value2
	q config --unset key1 key2
	q config  # print current config and config file path
	```

- Workflow management:

	```bash
	q workflow    # list available workflows
	q workflow --add /path/to/module.py   # add workflow module (can be a file or module path)
	q workflow --rm workflow_module_name  # remove by module name
	```

- Tool management:

	```bash
	q tool    # list available tools
	q tool --add some.module.or.path     # add tool module
	q tool --rm tool_module_name         # remove tool by module name
	```

Notes:

- Directory arguments accept filesystem paths (they are parsed as `Path`).
- Many `--add` flags accept multiple values; pass several entries separated by spaces.
- `--extra_tools` expects a comma-separated list when given as a single string.

For full CLI help and available options, run `q -h` or `q <subcommand> -h`.