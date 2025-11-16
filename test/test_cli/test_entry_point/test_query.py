import os
from pathlib import Path
from q.cli.entry_point import query


def test_query():
    query("what's the name of employee 123532", extra_tool_names=["think", "employees"], working_dir=Path(__file__).parent / "chat_testdata")
