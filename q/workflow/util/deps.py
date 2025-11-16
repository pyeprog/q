from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

from q.workflow.agent.config import ToolMap
from q.workflow.util.output import DefaultPrinter, ExtraParam, Printer


@dataclass
class BaseDeps:
    tool_map: ToolMap = field(default_factory=dict)
    extra_tool_names: Sequence[str] = field(default_factory=list)
    console: Printer = field(default_factory=DefaultPrinter)
    gen_agent_extra_param: Callable[[str], ExtraParam] = field(default=lambda _: ExtraParam())
    working_dir: Path = field(default_factory=Path.cwd)