from pydantic_ai.messages import FunctionToolResultEvent, ToolReturnPart
import pytest

from q.workflow.agent.util import agent_event_stream_handler


async def mock_async_stream(_list):
    for item in _list:
        yield item


@pytest.mark.asyncio
async def test_agent_event_stream_handler():
    function_tool_result_handled = False

    def handle_function_tool_result_event(e: FunctionToolResultEvent):
        nonlocal function_tool_result_handled
        function_tool_result_handled = True

    handler = agent_event_stream_handler([handle_function_tool_result_event])
    mock_stream = mock_async_stream(
        [FunctionToolResultEvent(result=ToolReturnPart(tool_name="mock", content="nothing"))]
    )
    await handler(None, mock_stream)  # type: ignore

    assert function_tool_result_handled
