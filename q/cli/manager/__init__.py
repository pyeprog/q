from typing import Callable

from pydantic_ai import AbstractToolset, ToolsetFunc
from q.workflow.agent.config import ToolMap


class GlobalToolMap(ToolMap):
    @classmethod
    def get[T](cls, tool_name: str, default: T | None = None, /) -> Callable | AbstractToolset | ToolsetFunc | T | None:
        # import only when tool map is used, and when it is used, current working directory must have .env file,
        # thus some internal tool like tavily will be initialized correctly, which happens inside tool_manager.
        from q.cli.manager.module.tool import tool_manager
        from q.cli.manager.mcp import mcp_manager

        if tool := tool_manager.tool_map.get(tool_name):
            return tool

        elif mcp := mcp_manager.get(tool_name):
            return mcp

        return default
