from pathlib import Path

import pytest

from q.cli.entry_point import ls


@pytest.mark.skip("run it in terminal manually")
def test_ls():
    path = Path(__file__).parent / "research_testdata1"
    ls(directory=path, snapshot=-1, field="reviser_message_history")
