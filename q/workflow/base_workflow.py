from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from pathlib import Path

from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode, End
from pydantic_graph.persistence import BaseStatePersistence

from q.workflow.util.deps import BaseDeps
from q.workflow.util.node import NodeToHalt


@dataclass
class State: ...


class BaseWorkflow(ABC):
    def __init__(self, deps: BaseDeps) -> None:
        self.deps = deps

    @classmethod
    @abstractmethod
    def graph(cls) -> Graph[State, BaseDeps]:
        raise NotImplementedError

    @abstractmethod
    def persistence(self) -> BaseStatePersistence:
        raise NotImplementedError

    @abstractmethod
    async def recover(self, user_input: str) -> tuple[State, BaseNode[State, BaseDeps]]:
        raise NotImplementedError

    def entry(self, *args, **kwargs):
        asyncio.run(self.run(*args, **kwargs))

    async def run(self, user_input: str) -> None:
        _graph = self.graph()
        _persistence = self.persistence()
        _state, _node = await self.recover(user_input)

        async with _graph.iter(_node, state=_state, persistence=_persistence, deps=self.deps) as run:
            while _node := await run.next():
                if issubclass(type(_node), NodeToHalt):
                    break
                elif isinstance(_node, End):
                    break
