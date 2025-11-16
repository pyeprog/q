from typing import Callable, Protocol


class ToolMap(Protocol):
    def get[T](self, tool_name: str, default: T | None = None, /) -> Callable | T | None: ...
