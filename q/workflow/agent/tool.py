from pathlib import Path
from dotenv import load_dotenv
from pydantic_ai import Tool
from ddgs import DDGS
from typing import Callable, Literal
from pydantic.main import BaseModel


class Thought(BaseModel):
    description: str
    importance: Literal["low", "medium", "high"]


def think_tool(thoughts: list[Thought]) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        thoughts (list[Thought]): A list of Thought objects representing the current
            chain of reasoning, research findings, and strategic considerations to
            be analyzed and reflected upon.
    Returns:
        str: signifying the completion of the reflection process.
    """

    return f"Reflection complete. {len(thoughts)} thoughts considered."


def create_tavily_search_tool(max_retries: int | None = None):
    from pydantic_ai.common_tools.tavily import TavilySearchTool
    from tavily.async_tavily import AsyncTavilyClient

    load_dotenv(Path.cwd() / ".env")

    return Tool(
        TavilySearchTool(client=AsyncTavilyClient()).__call__,
        name="tavily_web_search",
        description="Searches the web for the given query and returns the results. This tool is powerful but not free, use wisely.",
        max_retries=max_retries,
    )


def create_duckduckgo_search_tool(max_results: int = 5, max_retries: int | None = None):
    from pydantic_ai.common_tools.duckduckgo import DuckDuckGoSearchTool

    return Tool(
        DuckDuckGoSearchTool(client=DDGS(), max_results=max_results).__call__,
        name="duckduckgo_web_search",
        description="Searches DuckDuckGo for the given query and returns the results. This tool is free to use.",
        max_retries=max_retries,
    )


class ToolMap:
    def __init__(self):
        self.dict = {
            "think": think_tool,
            "tavily_search": create_tavily_search_tool(),
            "tavily_search_3_retries": create_tavily_search_tool(max_retries=3),
            "duckduckgo_search": create_duckduckgo_search_tool(),
            "duckduckgo_search_3_retries": create_duckduckgo_search_tool(max_retries=3),
            "duckduckgo_search_extensively": create_duckduckgo_search_tool(max_results=30, max_retries=3),
        }

    def get[T](self, key: str, default: T | None = None) -> Callable | T:
        return self.dict.get(key, default)
