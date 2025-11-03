from dataclasses import dataclass
from pydantic.main import BaseModel
from pydantic_graph.nodes import BaseNode, GraphRunContext

from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.util.deps import BaseDeps


class BackToRequirementRevising(BaseModel):
    feedback: str


class BackToResearchPlanning(BaseModel):
    feedback: str


class BackToResearchConducting(BaseModel):
    feedback: str


class SubmitResearchReport(BaseModel):
    report: str


@dataclass
class Halt(BaseNode[DeepResearchState, BaseDeps]):
    review: BackToRequirementRevising | BackToResearchPlanning | BackToResearchConducting | SubmitResearchReport

    async def run(self, ctx: GraphRunContext) -> "Halt":
        return self
