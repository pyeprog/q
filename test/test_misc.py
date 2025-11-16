import pytest
from q.workflow.agent.internal_tool import create_duckduckgo_search_tool
from q.workflow.util.misc import unique


def test_unique():
    tools = [create_duckduckgo_search_tool(), create_duckduckgo_search_tool()]
    with pytest.raises(Exception):
        unique(tools)

    assert len(unique(tools, key=lambda tool: tool.name)) == 1
