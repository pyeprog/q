from functools import cached_property
from q.workflow.util.typing import AgentConfigMap
from faker import Faker


from abc import ABC, abstractmethod


class ConfigurableNode(ABC):
    @classmethod
    @abstractmethod
    def agent_config(cls) -> AgentConfigMap:
        raise NotImplementedError


class NodeToHalt:
    pass


class Anthropomorphic:
    @cached_property
    def human_name(self) -> str:
        return Faker().name()
