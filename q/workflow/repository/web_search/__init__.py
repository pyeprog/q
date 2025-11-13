from pathlib import Path
from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode
from pydantic_graph.persistence.file import FileStatePersistence
from q.workflow.base_workflow import BaseWorkflow
from q.workflow.persistence import PERSISTENCE_FILENAME, FileLatestSnapshotPersistence
from q.workflow.repository.web_search.search import Halt, Searcher
from q.workflow.repository.web_search.state import State
from q.workflow.util.deps import BaseDeps


class SearchWorkflow(BaseWorkflow):
    @classmethod
    def graph(cls) -> Graph[State, BaseDeps]:
        return Graph(nodes=(Searcher, Halt), state_type=State)

    def persistence(self) -> FileStatePersistence:
        persistence = FileLatestSnapshotPersistence(Path(PERSISTENCE_FILENAME))
        persistence.set_graph_types(self.graph())
        return persistence

    async def recover(self, user_input: str) -> tuple[State, BaseNode[State, BaseDeps]]:
        if snapshot := await self.persistence().load_next():
            state = snapshot.state
        else:
            state = State()

        node = Searcher(user_input)

        return state, node
