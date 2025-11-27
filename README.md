# Q

## What is it?
"q" means query, which is a cli for agent application, including simple chatting, workflow, agentic action and more.

## Why should one make another AI frontend?
There are several types of AI frontend, all of them choose textbox as interface, but they differ in how LLM works and how it interacts with hosting environment.

In case of how LLM works, there're 3 types.
1. single LLM worker, who use tools and talk to user directly. there's no complicate process underneath.
2. workflow, meaning there're several LLMs and calculating steps working with each other, and how they interact with each other is defined by end user.
3. agentic app, meaning there's several LLMs working with each other, and they determine how to interact with each other by themselves.

Most applications land on "single LLM worker type" or "agentic app", in which you will find a strong agent group (with one or more LLM under the hood) to work with and no way to define the workflow for more complex task.

And you will find workflow orchestrating available platform like n8n, windmill, huginn, node-red, etc in which you can define your workflow with a drag-and-drop style interface.

> TODO: create concrete usage demonstration

In either case, it's not flexible enough. Apparently, you can't do workflow design befitting your very need when you have a general LLM or agent app. Moreover, it's limitted to work on orchestrating platform, at least you can't do crazy things with it, like those you can do with claude code, and those platforms are not so easy to config neither.

I'd like to have a frontend easy to use, to create complex workflow(even implement your own agentic flow, like deep-research or claude-code), to do some crazy thing on your host envionment( everything you can do with python, you can do with q), and it's mainly designed for programmer.


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