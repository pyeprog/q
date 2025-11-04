from dataclasses import dataclass
from pydantic_graph.graph import Graph, BaseStatePersistence, BaseNode
from pydantic_graph.nodes import End, GraphRunContext
from pydantic_graph.persistence.in_mem import SimpleStatePersistence
from q.workflow.base_workflow import BaseWorkflow
from q.workflow.util.deps import BaseDeps


@dataclass
class State:
    pass


@dataclass
class SayHi(BaseNode[State, BaseDeps]):
    input_: str

    async def run(self, ctx: GraphRunContext[State, BaseDeps]) -> End[str]:
        content = f"hi, {self.input_}"
        print(content)
        return End(content)


class MockFlow(BaseWorkflow):
    def graph(self) -> Graph[State, BaseDeps]:
        return Graph(nodes=(SayHi,), state_type=State)

    def persistence(self) -> BaseStatePersistence:
        persistence = SimpleStatePersistence()
        persistence.set_graph_types(self.graph())
        return persistence

    async def recover(self, user_input: str) -> tuple[State, BaseNode[State, BaseDeps]]:
        state = State()
        node = SayHi(user_input)

        return state, node
