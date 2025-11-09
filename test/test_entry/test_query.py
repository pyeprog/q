import os
from pathlib import Path
from q.cli.entry_point import query


def test_query():
    os.chdir(Path(__file__).parent / "chat_testdata")
    query("what's the name of employee 123532", extra_tools="think_tool, employees, employees")
