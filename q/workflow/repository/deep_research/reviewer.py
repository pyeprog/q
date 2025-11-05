from dataclasses import dataclass

from pydantic_ai.agent import Agent
from pydantic_ai.format_prompt import format_as_xml
from pydantic_graph.nodes import BaseNode, GraphRunContext

from q.workflow.agent.config import AgentConfig
from q.workflow.repository.deep_research.halt import (
    BackToRequirementRevising,
    BackToResearchConducting,
    BackToResearchPlanning,
    Halt,
    SubmitResearchReport,
)
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.agent.prompt import Instruction
from q.workflow.util.config import load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.util.node import ConfigurableNode
from q.workflow.util.typing import AgentConfigMap


@dataclass
class Review(BaseNode[DeepResearchState, BaseDeps], ConfigurableNode):
    research_report: str

    async def run(self, ctx: GraphRunContext[DeepResearchState, BaseDeps]) -> Halt:
        config = load_config().get_agent_config("reviewer")
        agent = Agent(
            model=config.model,
            instructions=self.instruction,
            tools=config.tools + ctx.deps.extra_tools,
            output_type=BackToRequirementRevising
            | BackToResearchConducting
            | BackToResearchPlanning
            | SubmitResearchReport,
            name="reviewer",
        )

        input_ = format_as_xml(
            {
                "origin user requirements": ctx.state.user_requirement,
                "research plan": ctx.state.research_plan,
                "research report": self.research_report,
            }
        )

        response = await agent.run(input_)

        if isinstance(
            response.output,
            (
                BackToRequirementRevising,
                BackToResearchConducting,
                BackToResearchPlanning,
            ),
        ):
            ctx.deps.console.set_title(type(response.output).__name__).print(response.output.feedback)
        else:
            ctx.deps.console.set_title("Research Done").print(response.output.report)

        return Halt(response.output)

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {"reviewer": AgentConfig(tool_names=["think_tool"])}

    @property
    def instruction(self) -> str:
        _instruction = Instruction(
            role="You are a senior researcher and has ability and taste to evaluate research report",
            task="Given origin user requirements, research plan(a set of leading questions) and research report, your job is to decide whether the report is good enough to submit. If not, you should decide which step we should go back to, whether it's user requirement revising, research planning or research conducting. You should attach your feedback to this step as well",
            context=[
                "the research steps are user requirement revising, research planning(ask questions), research conducting"
            ],
            output_formats=["plain text without markdown decoration, such as bold, italic and so on"],
            guidelines=[
                "your feedback should be specific and concrete. It's not enough to say a report is incomplete or missing critical information, you should point out what is missing, what should be added. Vague and abstract words are not welcome.",
                "don't be finicky or nitpicking, only focus on important and meaningful aspects of the report. Ignore those meaningless or trivial.",
            ],
        )

        return format_as_xml(_instruction)
