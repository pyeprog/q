from dataclasses import dataclass, field
from typing import Callable

from q.workflow.util.output import DefaultPrinter, Printer

        

@dataclass
class BaseDeps:
    extra_tools: list[Callable] = field(default_factory=list)
    console: Printer = field(default_factory=DefaultPrinter)

