import pytest
from q.cli.manager import GlobalToolMap
from q.workflow.agent.config import AgentConfig


def test_specifying_tools():
    config = AgentConfig(tool_names={"think", "tavily_search_3_retries", "duckduckgo_search_3_retries"})
    tools = config.tools(GlobalToolMap)
    assert len(tools) == 3


def test_specifying_extra_tools():
    config = AgentConfig(tool_names={"think"})
    extra_tool_names = ["tavily_search_3_retries", "duckduckgo_search_3_retries"]
    tools = config.tools(GlobalToolMap, extra_tool_names=extra_tool_names)
    assert len(tools) == 3


def test_given_wrong_tool_name():
    config = AgentConfig(tool_names={"not-even-exist"})

    with pytest.raises(AssertionError):
        config.tools(GlobalToolMap)

