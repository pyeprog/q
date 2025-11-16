import tempfile
from pathlib import Path
from q.cli.config import CentralizedConfig


TMP_PATH = Path(tempfile.gettempdir())


def test_init_file_creates_file_if_not_exists():
    config = CentralizedConfig(TMP_PATH / "test_config.toml")
    assert config.file_path.exists()
    config.file_path.unlink()  # Clean up
    assert not config.file_path.exists()


def test_set_updates_config():
    config = CentralizedConfig(TMP_PATH / "test_config.toml")
    config.set({"OPENROUTER_API_KEY": "new_key"})
    assert config.config["OPENROUTER_API_KEY"] == "new_key"
    config.file_path.unlink()  # Clean up


def test_unset_sets_placeholder():
    config = CentralizedConfig(TMP_PATH / "test_config.toml")
    config.set({"TAVILY_API_KEY": "some_key"})
    config.unset(["TAVILY_API_KEY"])
    assert config.config["TAVILY_API_KEY"] == CentralizedConfig.PLACEHOLDER
    config.file_path.unlink()  # Clean up


def test_to_env_file_creates_correct_env_file(tmp_path):
    config = CentralizedConfig(tmp_path / "test_config.toml")
    config.set({"OPENROUTER_API_KEY": "key_value"})
    env_file_path = tmp_path / ".env"
    config.to_env_file(env_file_path)
    assert env_file_path.read_text() == "OPENROUTER_API_KEY=key_value"
