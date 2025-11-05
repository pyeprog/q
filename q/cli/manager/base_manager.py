from abc import ABC
from dataclasses import dataclass
import importlib
import os
from pathlib import Path
import shutil
import sys
from types import ModuleType


@dataclass
class Module:
    mod: ModuleType
    mod_name: str
    mod_path: Path  # either a python file path or a module directory path


class BaseManager(ABC):
    def __init__(self, dir_path: str | Path) -> None:
        self.dir_path = Path(dir_path)
        if not self.dir_path.exists():
            self.dir_path.mkdir(exist_ok=True, parents=True)

        dir_path_str = str(self.dir_path.absolute())
        if dir_path_str not in sys.path:
            sys.path.append(dir_path_str)

    @staticmethod
    def rm(file_or_dir: str | Path):
        path = Path(file_or_dir)
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def cp(src: Path, dst: Path):
        copy_method = shutil.copy if src.is_file else shutil.copytree
        copy_method(src=src, dst=dst)

    @property
    def modules(self) -> list[Module]:
        mods: list[Module] = []

        for entry in os.listdir(self.dir_path):
            if entry.startswith("__") and entry.endswith("__") or entry.startswith("."):
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
                self.rm(path)

                continue

            mods.append(Module(mod=mod, mod_name=mod_name, mod_path=self.dir_path / entry))

        return mods

    def rm_modules(self, mod_names: list[str]):
        module_map = {m.mod_name: m for m in self.modules}
        for target_mod_name in mod_names:
            if target_mod_name not in module_map:
                continue

            self.rm(module_map[target_mod_name].mod_path)

    @staticmethod
    def is_module(path: Path) -> bool:
        return (path.is_file() and str(path).endswith(".py")) or (path.is_dir() and (path / "__init__.py").is_file())

    def add_modules(self, mod_paths: list[str | Path]):
        # add modules to certain directory
        for src_path in mod_paths:
            src_path = Path(src_path)

            if not self.is_module(src_path):
                # it's not valid python module
                continue

            # otherwise, it's valid python module, copy them to the workflow directory
            self.cp(src=src_path, dst=self.dir_path)

        # no need for a further check of module's content
        # if it's not valid, it might be removed when walk through the directory
