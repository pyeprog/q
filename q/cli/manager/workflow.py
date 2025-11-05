from copy import deepcopy
from dataclasses import asdict, dataclass
import inspect
from types import ModuleType

from q.cli.constant import CONFIG_HOME
from q.cli.manager.base_manager import BaseManager, Module
from q.workflow.base_workflow import BaseWorkflow
from q.workflow.repository import WORKFLOW_MAP


@dataclass
class WorkflowModule(Module):
    workflow_classes: list[type[BaseWorkflow]]


class WorkflowManager(BaseManager):
    @property
    def modules(self) -> list[WorkflowModule]:
        modules: list[WorkflowModule] = []

        for module in super().modules:
            if workflow_classes := self._workflow_classes(module.mod):
                # this module has several workflow classes, then it's the valid workflow module
                modules.append(
                    WorkflowModule(
                        workflow_classes=workflow_classes,
                        mod=module.mod,
                        mod_name=module.mod_name,
                        mod_path=module.mod_path,
                    )
                )
            else:  # it contains no workflow class, it couldn't be the workflow module, remove it
                self.rm(module.mod_path)

        return modules

    @staticmethod
    def _workflow_classes(mod: ModuleType) -> list[type[BaseWorkflow]]:
        results: list[type[BaseWorkflow]] = []

        for attr_name in dir(mod):
            if attr_name.startswith("__") and attr_name.endswith("__") and len(attr_name) > 4:
                continue  # magic attr

            attr = getattr(mod, attr_name)
            if inspect.isclass(attr) and issubclass(attr, BaseWorkflow) and attr is not BaseWorkflow:
                results.append(attr)

        return results

    @property
    def workflow_map(self) -> dict[str, type[BaseWorkflow]]:
        _workflow_map: dict[str, type[BaseWorkflow]] = deepcopy(WORKFLOW_MAP)

        for module in self.modules:
            for cls in module.workflow_classes:
                _workflow_map[cls.__name__] = cls

        return _workflow_map


workflow_manager = WorkflowManager(CONFIG_HOME / "workflow")
