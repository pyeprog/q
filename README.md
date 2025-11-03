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

Answer these questions:

what should we config?
- keys of platforms
- default model

how should we config?
- open editor, edit then save
- set or unset them directly through cli

```bash
q config --set key1=value1 key2=value2
q config --unset key1 key2
q config  # print content of the config and path of the config file
```

## TODO

- [x] customized file persistence (inheritted from FileStatePersisence of pydantic_graph)
- [x] implement a default chatting workflow
- [x] implement the legacy deep research workflow
- [x] chatting entry point refining, including: 
    - [x] choose which workflow been used
    - [x] choose which tool been used
- [x] command for starting a conversation, setup workflow, agent config and env file
- [x] manage state history
    - [x] list versions and fields
    - [x] list each messages of a field
    - [x] extracting message to start a new conversation
- [x] command for config setting, unsetting, editing, listing, config includes platform keys
    - [x] make a dict for platform keys
    - [x] implement initializer for centralized config file, which is used to save keys
    - [x] implement for creating .env file for local query directory
- [ ] command for tool managing including installing / removing / listing
- [ ] command for workflow managing including installing / removing / listing
- [ ] improve response readability, consider delimiter / markdown enhancement / border

## cancelled
- [ ] switching to other workflow from origin one(reason: graph is not matched, thus we should choose a workflow while creating the conversation)
- [ ] edit message of a particular version of state(reason: it's not possible to make it readable and supporting adding, editing and deleting at the same time)