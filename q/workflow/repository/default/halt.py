from q.workflow.util.deps import BaseDeps
from q.workflow.repository.default.state import DefaultState


from pydantic_graph.nodes import BaseNode, GraphRunContext


from dataclasses import dataclass

from q.workflow.util.node import NodeToHalt


@dataclass
class Halt(BaseNode[DefaultState, BaseDeps], NodeToHalt):
    async def run(self, ctx: GraphRunContext[DefaultState]) -> "Halt":
        return Halt()
