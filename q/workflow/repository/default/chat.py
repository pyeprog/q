from q.workflow.agent.config import AgentConfig
from q.workflow.agent.util import agent_event_stream_handler
from q.workflow.repository.default.halt import Halt
from q.workflow.util.config import AgentConfigMap, ConfigurableNode, load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.repository.default.state import DefaultState


from pydantic_ai.agent import Agent
from pydantic_ai.messages import FunctionToolResultEvent
from pydantic_graph.nodes import BaseNode, GraphRunContext


from dataclasses import dataclass


@dataclass
class Chat(BaseNode[DefaultState, BaseDeps], ConfigurableNode):
    user_input: str

    async def run(self, ctx: GraphRunContext[DefaultState, BaseDeps]) -> Halt:
        agent_config = load_config().get_agent_config("chatter")

        agent = Agent(
            model=agent_config.model,
            tools=agent_config.tools + ctx.deps.extra_tools,
            name="chatter",
        )

        def tool_result_event_handler(e: FunctionToolResultEvent):
            print(f"[Tool] {self.__class__.__name__} calls {e.tool_call_id!r}")

        response = await agent.run(
            self.user_input,
            message_history=ctx.state.message_history,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
        )

        ctx.state.message_history += response.new_messages()
        print(response.output)

        return Halt()

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {"chatter": AgentConfig()}
