from dataclasses import dataclass
from typing import ClassVar, Literal

from pydantic_ai.agent import Agent
from pydantic_ai.format_prompt import format_as_xml
from pydantic_graph.nodes import BaseNode, GraphRunContext

from q.workflow.agent.config import AgentConfig
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.agent.prompt import Instruction
from q.workflow.util.config import load_config
from q.workflow.util.deps import BaseDeps
from q.workflow.util.node import ConfigurableNode, NodeToHalt
from q.workflow.util.typing import AgentConfigMap
from pydantic.main import BaseModel


class DeepenResearch(BaseModel):
    """deepen research(redo some part of the research) if user requires"""

    where_to_start: Literal["requirement_revising", "research_planning", "research_conducting"]
    feedback: str


class ContinueReviewing(BaseModel):
    """continue reviewing based on current research report"""

    review_result: str


@dataclass
class Review(BaseNode[DeepResearchState, BaseDeps], ConfigurableNode, NodeToHalt):
    user_input: str | None = None
    next_start: DeepenResearch | ContinueReviewing | None = None
    agent_name: ClassVar[str] = "reviewer"

    async def run(self, ctx: GraphRunContext[DeepResearchState, BaseDeps]) -> "Review":
        config = load_config(ctx.deps.working_dir).get_agent_config(self.agent_name)
        agent = Agent(
            model=config.model,
            system_prompt=self.sys_prompt,
            tools=config.tools(ctx.deps.tool_map, extra_tool_names=ctx.deps.extra_tool_names),
            output_type=DeepenResearch | ContinueReviewing,
            name=self.agent_name,
        )

        input_ = format_as_xml(
            {
                "origin user requirements": ctx.state.user_requirement,
                "research plan": ctx.state.research_plan,
                "research report": ctx.state.research_report,
                "user's further requirement": self.user_input,
            }
        )

        response = await agent.run(input_, message_history=ctx.state.reviewer_message_history)

        ctx.state.reviewer_message_history += response.new_messages()

        if isinstance(response.output, DeepenResearch):
            ctx.deps.console.print(
                f"BACK TO STEP: {response.output.where_to_start}\n{response.output.feedback}",
                extra_param=ctx.deps.gen_agent_extra_param(type(response.output).__name__),
            )

        else:  # ContinueReviewing
            ctx.deps.console.print(
                response.output.review_result,
                extra_param=ctx.deps.gen_agent_extra_param(type(response.output).__name__),
            )

        return Review(next_start=response.output)

    @classmethod
    def agent_config(cls) -> AgentConfigMap:
        return {cls.agent_name: AgentConfig(tool_names={"think"})}

    @property
    def sys_prompt(self) -> str:
        prompt = Instruction(
            role="You are an expert academic peer reviewer, specializing in critical analysis, methodological rigor, and scientific communication. Your role is to uphold the highest standards of research quality and integrity, applying your expertise to specific user-assigned tasks.",
            task="Your primary task is to execute specific review assignments provided by the user, based on a received research report. These assignments will vary, but will always involve critically analyzing aspects of the report (e.g., methodology, results, discussion, writing style, ethical considerations) to fulfill the user's particular request. Your goal is to deliver precise, actionable feedback or analysis tailored to the user's instructions, aimed at enhancing the report's quality or addressing specific concerns.",
            context=[
                "You will be reviewing reports typically intended for academic journals, conferences, internal organizational review, or general research evaluation. Assume that the authors are experts in their field but may benefit from an objective, external perspective. Your analysis or feedback will be provided directly to the user who assigned the task. Focus on the scientific content, rigor, and communication effectiveness within the scope of the user's request.",
                "the research process contains ascertaining user requirement, planning research, conducting actual researching",
            ],
            guidelines=[
                "Adhere to User Instructions: Always prioritize and execute the specific review tasks assigned by the user.",
                "Thoroughness: Examine relevant sections of the report—introduction, literature review, methodology, results, discussion, conclusion, and references—as required by the user's task, for coherence, accuracy, and completeness.",
                "Constructive Criticism: Provide feedback that is always helpful and actionable, focusing on improvement rather than mere criticism, where applicable to the assigned task.",
                "Referencing: Verify the accuracy, completeness, and relevance of citations, if this is part of the assigned task.",
                "Consistency: Check for internal consistency within the report, ensuring that conclusions are supported by the results and discussion, within the scope of the user's request.",
                "Clarity and Conciseness: Assess the clarity of writing, logical flow of arguments, and effective presentation of data (tables, figures), and suggest improvements for readability and impact, as requested by the user.",
                "Originality and Significance: Evaluate the report's contribution to its field, assessing its originality, novelty, and potential impact, if this is part of the assigned task.",
            ],
        )

        return format_as_xml(prompt)
