from pathlib import Path
from unittest.mock import patch

import pytest
from q.cli.entry_point import query
from q.cli.manager.mcp import StdioMCP, mcp_manager
from q.workflow.agent.internal_tool import InternalToolMap, think_tool
from q.workflow.agent.typing import ToolMap
from dataclasses import dataclass
from typing import Callable, Literal



@dataclass
class MockEmployee:
    name: str
    age: int
    gender: Literal["Male", "Female"]
    salary: int


def employees(id: str) -> MockEmployee:
    return MockEmployee(name="Jane Doe", age=38, gender="Female", salary=0)



class MockInternalToolMap(ToolMap):
    @classmethod
    def dict(cls):
        # keep the dict inside function instead of putting it under class scope directly.
        # in this way the tavily search tool will be initialized only when we run the query and only at that moment,
        # it will be initialized correctly, cause there's an .env file under working directory at that time.
        # If we put it under class scope, it will be fired in import-time, which will cause bugs.
        return {
            "think": think_tool,
            "employees": employees,
        }

    @classmethod
    def keys(cls):
        return ["think", "employees"]

    @classmethod
    def get[T](cls, key: str, default: T | None = None, /) -> Callable | T:
        return cls.dict().get(key, default)


@patch.object(InternalToolMap, 'dict')
def test_query_with_tool(mock_method):
    mock_method.return_value = {
        "think": think_tool,
        "employees": employees,
    }
    query("what's the name of employee 123532", extra_tool_names=["think", "employees"], working_dir=Path(__file__).parent / "chat_testdata")


mock_mcp = StdioMCP(name='mock', command='uv', args=["run", "mcp-run-python", "stdio"])

# @pytest.mark.skip("Deno is not installed")
@patch.object(mcp_manager, 'mcps', [mock_mcp])
def test_query_with_mcp():
    query("what's the result of 2123123 / 1441", extra_tool_names=['mock'], working_dir=Path(__file__).parent / "chat_testdata")