from dataclasses import dataclass
from typing import ClassVar

from pydantic_ai.agent import Agent
from pydantic_ai.format_prompt import format_as_xml
from pydantic_ai.messages import FunctionToolResultEvent
from pydantic_graph.nodes import BaseNode, GraphRunContext
from q.workflow.agent.config import AgentConfig
from q.workflow.repository.deep_research.superviser import Supervise

from q.workflow.agent.util import (
    agent_event_stream_handler,
)
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.agent.prompt import Instruction
from q.workflow.util.config import load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.util.node import Anthropomorphic, ConfigurableNode
from q.workflow.util.output import ExtraParam
from q.workflow.util.typing import AgentConfigMap


@dataclass
class Plan(BaseNode[DeepResearchState, BaseDeps], ConfigurableNode, Anthropomorphic):
    user_requirement: str
    agent_name: ClassVar[str] = "planner"

    async def run(self, ctx: GraphRunContext[DeepResearchState, BaseDeps]) -> Supervise:
        def tool_result_event_handler(e: FunctionToolResultEvent):
            ctx.deps.console.print(
                f"🧙[bold magenta]{self.__class__.__name__}[/]([green]{self.human_name}[/]) 🤙 🛠️[bold cyan]{e.result.tool_name}[/]",
                extra_param=ExtraParam(markdownify=False),
            )

        config = load_config(ctx.deps.working_dir).get_agent_config(self.agent_name)

        agent = Agent(
            model=config.model,
            system_prompt=self.sys_prompt,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
            tools=config.tools(ctx.deps.tool_map, extra_tool_names=ctx.deps.extra_tool_names),
            name=self.agent_name,
        )

        response = await agent.run(self.user_requirement, message_history=ctx.state.research_plan)
        ctx.state.research_plan += response.new_messages()[1:]  # ignore the request message

        ctx.deps.console.print(response.output, extra_param=ctx.deps.gen_agent_extra_param(self.agent_name))

        return Supervise(response.output)

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {cls.agent_name: AgentConfig()}

    @property
    def sys_prompt(self) -> str:
        prompt = Instruction(
            role="You are a research planner",
            task="You will be given a set of user requirements. Your job is to translate these requirements into a research plan which should be in form of a set of detailed and concrete research questions",
            assumptions=[
                "the user requirements is detailed and complete",
                "the set of question you give out will guide further research, if the questions are well put, following research will result in high quality conclusion",
                "the following research on your questions is time and resource consuming.",
            ],
            guidelines=[
                "you should include all known user preferences and explicitly list key attributes or dimensions to consider",
                "Fill in Unstated But Necessary Dimensions as Open-Ended",
                "Avoid Unwarranted Assumptions: If the user has not provided a particular detail, do not invent one. Instead, state the lack of specification and guide the researcher to treat it as flexible or accept all possible options.",
                "Phrase the request from the perspective of the user.",
            ],
            output_formats=[
                "a set of researching questions",
                "plain text, no markdown decoration",
            ],
            taboos=["The questions raised is about subjective feeling or personal taste"],
        )

        return format_as_xml(prompt)
