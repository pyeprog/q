from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

from rich.style import Style


@runtime_checkable
class Printable(Protocol):
    def __str__(self) -> str: ...


@dataclass
class PanelParam:
    title: str
    border_style: Style | str
    title_align: Literal["left", "center", "right"] = field(default="left")


@dataclass
class ExtraParam:
    panel_param: PanelParam | None = field(default=None)
    markdownify: bool = field(default=True)


class Printer(ABC):
    @abstractmethod
    def print(
        self,
        *objects: Printable,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        extra_param: ExtraParam | None = None,
    ) -> None: ...


class DefaultPrinter(Printer):
    def print(
        self,
        *objects: Printable,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        extra_param: ExtraParam | None = None,
    ) -> None:
        print(*objects, sep=sep, end=end)
