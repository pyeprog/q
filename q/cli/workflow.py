# workflow manager
# 1. init directory
# 2. iterate through the directory and fetch each workflows
# 3. use workflow file or mod inside the workflow directory
# 4. remove workflow
# 5. add workflow

from copy import deepcopy
from dataclasses import dataclass
import inspect
import os
import shutil
import sys
from pathlib import Path
from types import ModuleType
import importlib

from cyclopts.argument.utils import startswith
from q.cli.constant import CONFIG_HOME
from q.workflow.base_workflow import BaseWorkflow
from q.workflow.repository import WORKFLOW_MAP

@dataclass
class WorkflowModule:
    path: Path  # file path or dir path
    mod_name: str
    mod: ModuleType
    workflow_classes: list[type[BaseWorkflow]]


class WorkflowManager:
    def __init__(self, dir_path: str | Path) -> None:
        self.dir_path = Path(dir_path)
        if not self.dir_path.exists():
            self.dir_path.mkdir(exist_ok=True, parents=True)

        dir_path_str = str(self.dir_path.absolute())
        if dir_path_str not in sys.path:
            sys.path.append(dir_path_str)
            
    @staticmethod
    def _rm(file_or_dir: str | Path):
        path = Path(file_or_dir)
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path, ignore_errors=True)
            
    @property
    def workflow_modules(self) -> list[WorkflowModule]:
        modules: list[WorkflowModule] = []

        for entry in os.listdir(self.dir_path):
            if (entry.startswith("__") and entry.endswith("__")
                or entry.startswith('.')):
                # skip __x__ files and hidden files
                continue

            path = self.dir_path / entry
            mod_name = entry.removesuffix(".py")
            try:
                mod = importlib.import_module(mod_name)

            except Exception as e:
                # if it's not importable then it's not valid python module
                print(e, file=sys.stderr)

                # we should delete this file
                self._rm(path)

                continue

            if workflow_classes := self._workflow_classes(mod):
                # this module has several workflow classes, then it's the valid workflow module
                modules.append(WorkflowModule(path=self.dir_path / entry,
                               mod=mod,
                               mod_name=mod_name,
                               workflow_classes=workflow_classes))
            else:
                # it contains no workflow class, it couldn't be the workflow module, remove it
                self._rm(path)

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

        for module in self.workflow_modules:
            for cls in module.workflow_classes:
                _workflow_map[cls.__name__] = cls
                
        return _workflow_map


    def rm_workflow_modules(self, workflow_mod_names: list[str]):
        module_map = {m.mod_name: m for m in self.workflow_modules}
        for target_mod_name in workflow_mod_names:
            if target_mod_name not in module_map:
                continue

            path = module_map[target_mod_name].path

            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path, ignore_errors=True)
                
    def add_workflow_modules(self, workflow_mod_paths: list[str | Path]):
        # add workflow modules to workflow directory
        for src_path in workflow_mod_paths:
            src_path = Path(src_path)

            if not ((src_path.is_file() and str(src_path).endswith('.py'))
                    or (src_path.is_dir() and (src_path / "__init__.py").is_file())):
                # it's not valid python module
                continue
            
            # otherwise, copy them to the workflow directory
            if src_path.is_file():
                shutil.copy(src=src_path, dst=self.dir_path)
            else:  # is_dir
                shutil.copytree(src=src_path, dst=self.dir_path)

        # no need for a further workflow module check
        # if it's not valid workflow module, it might be removed when walk through the workflow directory

workflow_manager = WorkflowManager(CONFIG_HOME / "workflow")
