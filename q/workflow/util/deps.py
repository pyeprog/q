from dataclasses import dataclass, field
from typing import Callable

from q.workflow.util.output import DefaultPrinter, ExtraParam, Printer


@dataclass
class BaseDeps:
    extra_tools: list[Callable] = field(default_factory=list)
    console: Printer = field(default_factory=DefaultPrinter)
    gen_agent_extra_param: Callable[[str], ExtraParam] = field(default=lambda _: ExtraParam())
