from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass

from pydantic_graph.graph import Graph
from pydantic_graph.nodes import BaseNode
from pydantic_graph.persistence import BaseStatePersistence

from q.workflow.util.deps import BaseDeps


@dataclass
class State: ...


class BaseWorkflow(ABC):
    def __init__(self, deps: BaseDeps | None = None) -> None:
        self.deps = deps or BaseDeps()

    @abstractmethod
    def graph(self) -> Graph:
        raise NotImplementedError

    @abstractmethod
    def persistence(self) -> BaseStatePersistence:
        raise NotImplementedError

    @abstractmethod
    async def recover(self, user_input: str) -> tuple[State, BaseNode]:
        raise NotImplementedError

    @abstractmethod
    async def run(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def entry(self, *args, **kwargs):
        asyncio.run(self.run(*args, **kwargs))
