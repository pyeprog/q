from contextlib import suppress
import hashlib
import json
import sys
import tomllib
from rich.color import ANSI_COLOR_NAMES
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style
import xml.etree.ElementTree as ET


from q.workflow.util.output import ExtraParam, PanelParam, Printable, Printer


ANSI_COLOR_MAP: dict[int, str] = {v: k for k, v in ANSI_COLOR_NAMES.items() if k not in {"black", "bright_black"}}


def pick_color(content: str) -> str:
    color_idx = int(hashlib.sha256(content.encode("utf-8")).digest()[0])
    color_list = list(ANSI_COLOR_MAP.values())
    return color_list[color_idx % len(color_list)]


def panel_param_by_content(panel_title: str) -> PanelParam:
    return PanelParam(title=panel_title, border_style=Style(color=pick_color(panel_title), dim=False))


class CliConsole(Printer):
    def __init__(self, plain: bool = False) -> None:
        self._console = Console()
        self._plain = plain

    def is_json(self, s: str) -> bool:
        with suppress(Exception):
            json.loads(s)
            return True
        return False

    def is_toml(self, s: str) -> bool:
        with suppress(Exception):
            tomllib.loads(s)
            return True
        return False

    def is_xml(self, s: str) -> bool:
        with suppress(Exception):
            ET.fromstring(s)
            return True
        return False

    def is_markdown_or_yaml(self, s: str) -> bool:
        # Since almost no correct YAML processors exist(https://matrix.yaml.info/)
        # and we can't tell the difference between yaml and plain text using yaml lib in python
        # and yaml is not that difficult to read for human, thus we treat markdown and yaml as a whole
        # Moreover, plain text is a special kind of markdown, so markdown refers to markdown and plain text
        return not (self.is_json(s) or self.is_toml(s) or self.is_xml(s))

    def markdownify(self, s: str):
        string = s.strip()
        if string.startswith("```markdown") and string.endswith("```"):
            # sometimes ai agent will output content wrapped in redundant markdown block
            # we strip that off to make rich console work
            string = string.removeprefix("```markdown").removesuffix("```")

        return Markdown(string)

    def print(
        self,
        *objects: Printable,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        extra_param: ExtraParam | None = None,
    ) -> None:
        for content in objects:
            if not self._plain and sys.stdout.isatty() and isinstance(content, str):
                if extra_param and self.is_markdown_or_yaml(content) and extra_param.markdownify:
                    content = self.markdownify(content)

                if extra_param and extra_param.panel_param:
                    content = Panel(
                        content,
                        border_style=extra_param.panel_param.border_style,
                        title=extra_param.panel_param.title,
                        title_align=extra_param.panel_param.title_align,
                    )

            self._console.print(content, sep=sep, end=end, style=style)


console = CliConsole(plain=False)
