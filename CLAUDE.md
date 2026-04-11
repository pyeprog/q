# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Q ("query") is a Python CLI for AI agent applications. It supports simple chatting, custom workflows (multi-step LLM pipelines), and agentic flows. Users create "query directories" that hold config and conversation history, then interact via the `q` CLI.

## Development Commands

```bash
# Install dependencies (uses uv, Python 3.13)
uv sync

# Run the CLI
uv run q <subcommand>

# Run all tests
uv run pytest

# Run a single test file
uv run pytest test/test_misc.py

# Run a specific test
uv run pytest test/test_misc.py::test_function_name -v

# Lint
uv run ruff check .
```

## Architecture

### CLI Layer (`q/cli/`)
- `parser.py` — argparse definitions for all subcommands (`say`, `create`, `info`, `ls`, `config`, `workflow`, `tool`)
- `entry_point.py` — implementation of each subcommand; dispatched from `__init__.py` via `match args.command`
- `config.py` — `CentralizedConfig` class managing global config at `~/.query/config.toml` (API keys, editor, etc.)
- `console.py` — `CliConsole` wrapping Rich for formatted output
- `manager/` — module management for user-registered tools (`tool.py`), workflows (`workflow.py`), and MCP servers (`mcp.py`)

### Workflow Layer (`q/workflow/`)
- `base_workflow.py` — `BaseWorkflow` ABC that all workflows extend. Subclasses define a `Graph`, a persistence strategy, and a `recover()` method for resuming from saved state.
- Workflows are built on **pydantic-graph**: each workflow is a `Graph` of `BaseNode` subclasses with a shared state dataclass. Nodes run sequentially; the graph persists snapshots to `history.json` via `FileStatePersistence`.
- `repository/` — built-in workflows:
  - `default` — simple chat (`Chat` -> `Halt`)
  - `search` — web search workflow (`Searcher` -> `Halt`)
  - `research` — deep research multi-step flow (`Revise` -> `Plan` -> `Supervise` -> `Review`, with feedback loops)
- `agent/` — shared agent infrastructure:
  - `config.py` — `AgentConfig` (model selection, tool binding). Currently only supports OpenRouter as provider.
  - `prompt.py` — prompt templates
  - `internal_tool.py` — built-in tools available to agents
- `util/node.py` — mixins: `ConfigurableNode` (nodes with per-node agent config), `NodeToHalt` (signals workflow stop), `Anthropomorphic` (assigns human names via Faker)

### Key Concepts
- **Query directory**: a directory containing `workflow_config.json` (workflow name + per-node agent config), `.env` (API keys), and `history.json` (conversation snapshots). Created via `q create`.
- **Tool/Workflow modules**: users can register external Python modules as tools or workflows via `q tool --add` / `q workflow --rm`. These are persisted in `~/.query/`.
- **MCP support**: tools can also be MCP servers (Stdio, SSE, Streamable HTTP), added via JSON config through `q tool --add '{...}'`.

## Configuration
- Global config lives at `~/.query/config.toml` (managed by `q config`)
- Per-query config lives in the query directory as `workflow_config.json`
- Ruff line length is 120
