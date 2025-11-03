from q.workflow.util.deps import BaseDeps
from q.workflow.repository.default.state import DefaultState


from pydantic_graph.nodes import BaseNode, GraphRunContext


from dataclasses import dataclass


@dataclass
class Halt(BaseNode[DefaultState, BaseDeps]):
    async def run(self, ctx: GraphRunContext[DefaultState]) -> "Halt":
        return Halt()
