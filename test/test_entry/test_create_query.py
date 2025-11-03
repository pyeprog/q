from pathlib import Path
import shutil
import tempfile
from typing import Any, Generator

import pytest

from q.cli.entry_point import create_query


@pytest.fixture
def nonexisting_dir() -> Generator[Path, Any, Any]:
    path = Path(tempfile.gettempdir()) / "test_create_query"
    print(f"The test path: {path}")
    shutil.rmtree(path, ignore_errors=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def test_create(nonexisting_dir: Path):
    path = nonexisting_dir

    create_query(directory=path, workflow="research")

    assert path.exists()
    assert path.is_dir()
    env_file = path / ".env"
    assert env_file.exists()
    assert env_file.read_text()

    config_file = path / "agent_config.json"
    assert config_file.exists()
    assert config_file.read_text()
