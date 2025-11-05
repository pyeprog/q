import sys
from typing import Self
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from q.workflow.util.output import Printable



class MarkdownConsole:
    def __init__(self, plain: bool = False) -> None:
        self._console = Console(soft_wrap=True)
        self._title = ""
        self._plain = plain
        
    def set_title(self, title: str) -> Self:
        self._title = title
        return self
    
    def set_plain(self, plain: bool) -> Self:
        self._plain = plain
        return self
    
    def preprocess(self, s: str):
        string = s.strip()
        if string.startswith("```markdown") and string.endswith("```"):
            # unwrap the markdown content from the block
            string = string.removeprefix("```markdown").removesuffix("```")
            return Markdown(string)
    
        lines = string.split('\n')
        if any([line.startswith('# ') for line in lines]):
            return Markdown(string)
    
        return s # keep it unchanged in this case


    def print(self, any: Printable) -> None:
        content = any
        if not self._plain and sys.stdout.isatty() and isinstance(content, str):
            content = self.preprocess(content)
            content = Panel(content, border_style="dim", title=self._title, title_align="left")
        self._console.print(content)
        

console = MarkdownConsole()