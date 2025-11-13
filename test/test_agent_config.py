import pytest
from q.workflow.agent.config import AgentConfig


def test_specifying_tools():
    config = AgentConfig(tool_names=["think", "tavily_search_3_retries", "duckduckgo_search_3_retries"])
    assert isinstance(config.tools, list)
    assert len(config.tools) == 3


def test_given_wrong_tool_name():
    config = AgentConfig(tool_names=["not-even-exist"])

    with pytest.raises(AssertionError):
        config.tools
