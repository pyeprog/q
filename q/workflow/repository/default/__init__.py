from pathlib import Path

from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode

from q.workflow.base_workflow import BaseWorkflow
from q.workflow.persistence import PERSISTENCE_FILENAME
from pydantic_graph.persistence.file import FileStatePersistence
from q.workflow.util.deps import BaseDeps
from q.workflow.repository.default.state import DefaultState
from q.workflow.repository.default.chat import Chat
from q.workflow.repository.default.halt import Halt


class ChatWorkflow(BaseWorkflow):
    @classmethod
    def graph(cls) -> Graph[DefaultState, BaseDeps]:
        return Graph(nodes=(Chat, Halt), state_type=DefaultState)

    def persistence(self) -> FileStatePersistence:
        persistence = FileStatePersistence(self.deps.working_dir / PERSISTENCE_FILENAME)
        persistence.set_graph_types(self.graph())
        return persistence

    async def recover(self, user_input: str) -> tuple[DefaultState, BaseNode[DefaultState, BaseDeps]]:
        if snapshot := await self.persistence().load_next():
            state = snapshot.state
        else:
            state = DefaultState()

        node = Chat(user_input)

        return state, node
