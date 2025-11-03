from dataclasses import dataclass

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
from q.workflow.util.config import AgentConfigMap, ConfigurableNode, load_config
from q.workflow.util.deps import BaseDeps


@dataclass
class Plan(BaseNode[DeepResearchState, BaseDeps], ConfigurableNode):
    user_requirement: str

    async def run(self, ctx: GraphRunContext[DeepResearchState, BaseDeps]) -> Supervise:
        def tool_result_event_handler(e: FunctionToolResultEvent):
            print(f"[Tool] {self.__class__.__name__} calls {e.tool_call_id!r}")

        config = load_config().get_agent_config("planner")

        agent = Agent(
            model=config.model,
            instructions=self.instruction,
            event_stream_handler=agent_event_stream_handler([tool_result_event_handler]),
            tools=config.tools + ctx.deps.extra_tools,
            name="planner",
        )

        response = await agent.run(self.user_requirement, message_history=ctx.state.research_plan)
        ctx.state.research_plan += response.new_messages()[-1:]

        print(response.output)

        return Supervise(response.output)

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {"planner": AgentConfig()}

    def instruction(self) -> str:
        _instruction = Instruction(
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

        return format_as_xml(_instruction)
