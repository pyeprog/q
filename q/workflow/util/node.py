from q.workflow.util.typing import AgentConfigMap


from abc import ABC, abstractmethod


class ConfigurableNode(ABC):
    @classmethod
    @abstractmethod
    def agent_config(cls) -> AgentConfigMap:
        raise NotImplementedError


class NodeToHalt:
    pass
