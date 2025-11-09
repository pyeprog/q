from rich.console import Console
from q.cli.console import CliConsole
from q.workflow.util.output import ExtraParam


def test_print_markup_string():
    console = CliConsole()
    console.print(
        "[bold red]run this test in terminal, it should be in red[/]", extra_param=ExtraParam(markdownify=False)
    )
    Console().print("[bold red]comparing to this line of text, it should be in red[/]")
