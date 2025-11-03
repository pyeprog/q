from dataclasses import dataclass, field
from typing import Callable


@dataclass
class BaseDeps:
    extra_tools: list[Callable] = field(default_factory=list)
