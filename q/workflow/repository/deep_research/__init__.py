from pathlib import Path
from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode
from pydantic_graph.persistence.file import FileStatePersistence

from q.workflow.base_workflow import BaseWorkflow
from q.workflow.persistence import PERSISTENCE_FILENAME
from q.workflow.repository.deep_research.halt import (
    BackToRequirementRevising,
    BackToResearchConducting,
    BackToResearchPlanning,
    Halt,
)
from q.workflow.repository.deep_research.planner import Plan
from q.workflow.repository.deep_research.reviewer import Review
from q.workflow.repository.deep_research.reviser import Revise, UserRevise
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.repository.deep_research.superviser import Supervise
from q.workflow.util.deps import BaseDeps


class DeepResearchWorkflow(BaseWorkflow):
    @classmethod
    def graph(cls) -> Graph[DeepResearchState, BaseDeps]:
        return Graph(
            nodes=(Revise, UserRevise, Plan, Supervise, Review, Halt),
            state_type=DeepResearchState,
        )

    def persistence(self) -> FileStatePersistence:
        persistence = FileStatePersistence(Path(PERSISTENCE_FILENAME))
        persistence.set_graph_types(self.graph())
        return persistence

    async def recover(self, user_input: str) -> tuple[DeepResearchState, BaseNode[DeepResearchState, BaseDeps]]:
        if snapshot := await self.persistence().load_next():
            node = snapshot.node
            state = snapshot.state
        else:
            node = Revise(user_input)
            state = DeepResearchState()

        # special logic to go back to upstream node and do it again
        if isinstance(node, Halt):
            if isinstance(node.review, BackToRequirementRevising):
                node = Revise(node.review.feedback + "\n" + user_input)
            elif isinstance(node.review, BackToResearchPlanning):
                node = Plan(node.review.feedback + "\n" + user_input)
            elif isinstance(node.review, BackToResearchConducting):
                node = Supervise(node.review.feedback + "\n" + user_input)
            else:  # SubmitReport
                exit(0)

        elif isinstance(node, UserRevise):
            node.input_ = user_input

        return state, node
