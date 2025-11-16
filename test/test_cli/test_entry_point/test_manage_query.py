from pathlib import Path

from q.cli.entry_point import info, ls


def test_manage_query_ls():
    test_data_path = Path(__file__).parent / "research_testdata"
    ls(test_data_path, snapshot=-1, field="")


def test_manage_query_info():
    test_data_path = Path(__file__).parent / "research_testdata"
    info(test_data_path)
