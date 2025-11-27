### Version 0.1

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
- [x] command for workflow managing including installing / removing / listing
  - [x] init directory for workflows
  - [x] iterate through the directory and fetch each workflows
  - [x] use workflow file or mod inside the workflow directory
  - [x] remove workflow
  - [x] add workflow
- [x] command for tool managing including installing / removing / listing
  - [x] init directory for tools
  - [x] iterate through directory to list tools
  - [x] use tools (extra tool)
  - [x] rm tool modules
  - [x] add tool modules
- [x] improve response readability, consider delimiter / markdown enhancement / border
  - [x] make the "list" subcommand print table
  - [x] make the conversation return readable
    - [x] support markdown
    - [x] prettify markdown(fix bugs)
    - [x] separate input and output, mark the agent's name on the panel
    - [x] print content with panel when output to stdout, otherwise without panel
    - [x] make request and response be in panel with different color
  - [x] make tool calling & result print prettier
- [x] revising the research workflow printing
  - [x] change reviser to UserRevise to Planner
  - [x] change reviewer so that user can interact with the research result
  - [x] fix revising bug
    - [x] change instruction to system prompt
    - [x] fix revising history gone(no need, this is because status has became error then restart from scratch)
  - [x] fix ls to print all message
    - [x] predicate the xml format
- [x] support for reading in stdin


### Version 0.2
- [x] make editor configurable
- [x] register mcp and use mcp as tool
- [x] create an internal workflow of extensive internet searching
- [x] add extra tool option for create query subcommand
- [ ] add command for creating tool and workflow from template
- [ ] make the search workflow more useful
  - [ ] add citings
  - [ ] show search result
- [ ] support for file attach in chatting
- [ ] recover running after error occurs
- [ ] clarify how to "edit" the message history
- [ ] the last step of research workflow can't do work right, redesign the last part of the workflow to make it responding to user's need
- [ ] rewrite readme

### Future Version

- [ ] integrate vector database
- [ ] integrate memory management

