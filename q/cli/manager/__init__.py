from typing import Callable
from q.cli.manager.module.tool import tool_manager
from q.cli.manager.mcp import mcp_manager
from q.workflow.agent.config import ToolMap


def find_tools(tool_names: list[str], exclusive_tool_names: set[str] | None = None) -> list[Callable]:
    """find tools and mcps according to tool names, tools and mcps includes both internal ones and external ones

    Args:
        tools_str (str | None, optional): in format of "tool1,tool2,tool3,...". Defaults to None.
        exclusive_tool_names (set[str] | None, optional): tool names you don't want to fetch. Defaults to None.

    Returns:
        list[Callable]: list of tool functions, Tool objects and Mcp server objects
    """
    if not tool_names:
        return []

    tool_map = tool_manager.tool_map
    exclusive_tool_names = exclusive_tool_names or set()
    tools: list[Callable] = []

    for tool_name in tool_names:
        if tool_name in exclusive_tool_names:
            continue

        if tool := tool_map.get(tool_name):
            tools.append(tool)

        elif mcp := mcp_manager.get(tool_name):
            tools.append(mcp)

        else:
            raise ValueError(f"tool or mcp named '{tool_name}' not found")

    return tools


class GlobalToolMap(ToolMap):
    @classmethod
    def get[T](cls, tool_name: str, default: T | None = None, /) -> Callable | T | None:
        if tool := tool_manager.tool_map.get(tool_name):
            return tool

        elif mcp := mcp_manager.get(tool_name):
            return mcp

        return default
