from typing import Callable, Protocol

from pydantic_ai import AbstractToolset, ToolsetFunc


class ToolMap(Protocol):
    @classmethod
    def get[T](cls, tool_name: str, default: T | None = None, /) -> Callable | AbstractToolset | ToolsetFunc | T | None:
        ...
