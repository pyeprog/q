from importlib import import_module
from typing import Callable, Literal

from pydantic.fields import Field
from pydantic.main import BaseModel
from pydantic_ai.models import Model

from q.workflow.agent.util import open_router_model


class AgentConfig(BaseModel):
    provider: Literal["open_router"] = "open_router"
    model_name: str = "google/gemini-2.0-flash-001"  # for now , only support open_router model name
    tool_names: list[str] = Field(default_factory=list)

    @property
    def model(self) -> Model:
        assert self.provider == "open_router", "only open_router provider is supported for now"
        return open_router_model(self.model_name)

    @property
    def tools(self) -> list[Callable]:
        tool_module = import_module("q.workflow.agent.tool")
        return [getattr(tool_module, tool_name) for tool_name in self.tool_names if hasattr(tool_module, tool_name)]
