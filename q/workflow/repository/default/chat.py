from typing import ClassVar
from q.workflow.agent.config import AgentConfig
from q.workflow.agent.util import agent_event_stream_handler
from q.workflow.repository.default.halt import Halt
from q.workflow.util.config import load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.repository.default.state import DefaultState


from pydantic_ai.agent import Agent
from pydantic_ai.messages import FunctionToolResultEvent
from pydantic_graph.nodes import BaseNode, GraphRunContext


from dataclasses import dataclass

from q.workflow.util.misc import unique
from q.workflow.util.node import Anthropomorphic, ConfigurableNode
from q.workflow.util.output import ExtraParam
from q.workflow.util.typing import AgentConfigMap


@dataclass
class Chat(BaseNode[DefaultState, BaseDeps], ConfigurableNode, Anthropomorphic):
    user_input: str
    agent_name: ClassVar[str] = "chatter"

    async def run(self, ctx: GraphRunContext[DefaultState, BaseDeps]) -> Halt:
        agent_config = load_config().get_agent_config(self.agent_name)

        agent = Agent(
            model=agent_config.model,
            tools=unique(agent_config.tools + ctx.deps.extra_tools, key=lambda tool: tool.name),
            name=self.agent_name,
        )

        def tool_result_event_handler(e: FunctionToolResultEvent):
            ctx.deps.console.print(
                f"🧙[bold magenta]{self.__class__.__name__}[/]([green]{self.human_name}[/]) 🤙 🛠️[bold cyan]{e.result.tool_name}[/]",
                extra_param=ExtraParam(markdownify=False),
            )

        response = await agent.run(
            self.user_input,
            message_history=ctx.state.message_history,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
        )

        ctx.state.message_history += response.new_messages()
        ctx.deps.console.print(response.output, extra_param=ctx.deps.gen_agent_extra_param(self.agent_name))

        return Halt()

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {cls.agent_name: AgentConfig()}
