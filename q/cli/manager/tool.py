from copy import deepcopy
from dataclasses import dataclass
import inspect
from types import ModuleType
from typing import Callable

from q.cli.constant import CONFIG_HOME
from q.cli.manager.base_manager import BaseManager, Module
from q.workflow.agent.tool import ToolMap


@dataclass
class ToolModule(Module):
    tool_functions: list[Callable]


class ToolManager(BaseManager):
    @property
    def modules(self) -> list[ToolModule]:
        tool_modules: list[ToolModule] = []

        for module in super().modules:
            if tool_functions := self._tool_functions(module.mod):
                tool_modules.append(
                    ToolModule(
                        tool_functions=tool_functions,
                        mod=module.mod,
                        mod_name=module.mod_name,
                        mod_path=module.mod_path,
                    )
                )
            else:  # it contains no functions, it's probably garbage module, remove it
                self.rm(module.mod_path)

        return tool_modules

    @staticmethod
    def _tool_functions(mod: ModuleType) -> list[Callable]:
        functions: list[Callable] = []

        for entry in dir(mod):
            if entry.startswith("__") and entry.endswith("__") and len(entry) > 4:
                continue  # skip __x__ alike symbols

            if (attr := getattr(mod, entry)) and inspect.isfunction(attr):
                functions.append(attr)

        return functions

    @property
    def tool_map(self) -> dict[str, Callable]:
        _map: dict[str, Callable] = deepcopy(ToolMap().dict)

        for tool_module in self.modules:
            for tool_function in tool_module.tool_functions:
                _map.setdefault(tool_function.__name__, tool_function)

        return _map


tool_manager = ToolManager(CONFIG_HOME / "tool")
