from typing import Callable, Literal, Sequence

from pydantic.fields import Field
from pydantic.main import BaseModel
from pydantic_ai import AbstractToolset, ToolsetFunc
from pydantic_ai.models import Model

from q.workflow.agent.typing import ToolMap
from q.workflow.agent.util import open_router_model


class AgentConfig(BaseModel):
    provider: Literal["open_router"] = "open_router"
    model_name: str = "google/gemini-2.0-flash-001"  # for now , only support open_router model name
    tool_names: set[str] = Field(default_factory=set)

    @property
    def model(self) -> Model:
        assert self.provider == "open_router", "only open_router provider is supported for now"
        return open_router_model(self.model_name)

    def _find_tools(self, tool_map: ToolMap, extra_tool_names: Sequence[str] | None = None) -> list[Callable | AbstractToolset]:
        tools: list[Callable | AbstractToolset] = []
        for tool_name in self.tool_names.union(extra_tool_names or []):
            tool = tool_map.get(tool_name)
            assert tool, "tool '{tool_name}' is not found in given tool map"
            tools.append(tool)

        return tools

    def tools(self, tool_map: ToolMap, extra_tool_names: Sequence[str] | None = None) -> list[Callable]:
        tools = self._find_tools(tool_map=tool_map, extra_tool_names=extra_tool_names)
        return [tool for tool in tools if not isinstance(tool, AbstractToolset)]

    def toolsets(self, tool_map: ToolMap, extra_tool_names: Sequence[str] | None = None) -> list[AbstractToolset | ToolsetFunc]:
        tools = self._find_tools(tool_map=tool_map, extra_tool_names=extra_tool_names)
        return [tool for tool in tools if isinstance(tool, AbstractToolset)]
