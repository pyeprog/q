from pathlib import Path
from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode
from pydantic_graph.persistence.file import FileStatePersistence

from q.workflow.base_workflow import BaseWorkflow
from q.workflow.persistence import PERSISTENCE_FILENAME
from q.workflow.repository.deep_research.planner import Plan
from q.workflow.repository.deep_research.reviewer import DeepenResearch, Review
from q.workflow.repository.deep_research.reviser import Revise, UserRevise
from q.workflow.repository.deep_research.state import DeepResearchState
from q.workflow.repository.deep_research.superviser import Supervise
from q.workflow.util.deps import BaseDeps


class DeepResearchWorkflow(BaseWorkflow):
    @classmethod
    def graph(cls) -> Graph[DeepResearchState, BaseDeps]:
        return Graph(
            nodes=(Revise, UserRevise, Plan, Supervise, Review),
            state_type=DeepResearchState,
        )

    def persistence(self) -> FileStatePersistence:
        persistence = FileStatePersistence(self.deps.working_dir / PERSISTENCE_FILENAME)
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
        if isinstance(node, UserRevise):
            node.user_input = user_input

        elif isinstance(node, Review):
            if isinstance(node.next_start, DeepenResearch):
                match node.next_start.where_to_start:
                    case "requirement_revising":
                        node = Revise(node.next_start.feedback + "\n" + user_input)

                    case "research_planning":
                        node = Plan(node.next_start.feedback + "\n" + user_input)

                    case "research_conducting":
                        node = Supervise(node.next_start.feedback + "\n" + user_input)

            else:  # ContinueReviewing
                node = Review(user_input=user_input)

        return state, node
