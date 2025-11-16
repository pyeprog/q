# Q

"q" means query, which is a cli for agent application, including simple chatting, workflow, agentic action and more. 

## Features

1. q can register tools and work with them.
2. q can register workflows and work with them.
3. there're many tools and workflows you can choose from.
4. local directory as chat cache, you can config model, tools, workflow, even edit message history with chat cache.


## How to

### create a query

```bash
q c <path> --workflow default
ls -a <path>
# agent_config.json .env
```

```bash
q c <path> --w research -r <other-path>
ls -a <path>
# agent_config.json .env history.json
```

### chat with agent

```bash
cd <path>
q s "who are you?"
# I'm xxx model made by xxx company
```

### manage chatting history

```bash
cd <path>
q info <dir>
q info # default directory is current directory
# there are 23 versions of snapshot, index `[0-22]` or `latest` to retrive the last one, if not given, the default will be latest
# these fields are supported: a, b, c, d, .... if not given, the first field will be retrieve

q ls <dir> 
q ls # default directory is current directory
# snapshot = latest, field will the first one retrieved
# messages...

q ls --snapshot 3 
# snapshot = 3, field will be the first one retrieved
# messages... 

q ls --snapshot latest --field <name>
# snapshot = latest, field will be the <name>
# messages...
```

### config

```bash
q config --set key1=value1 key2=value2
q config --unset key1 key2
q config  # print content of the config and path of the config file
```

### workflow

```bash
q workflow # list all available workflows
q workflow --add <py-file-or-py-mod>
q workflow --rm <name>
```

### tool

```bash
q tool # list all available tools
q tool --add <py-file-or-py-mod>
q tool --rm <name>
```