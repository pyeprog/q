from pathlib import Path

import toml

from q.cli.constant import CONFIG_HOME


class CentralizedConfig:
    PLACEHOLDER = "(set-before-use)"

    CONFIG_TEMPLATE: dict = {
        "OPENROUTER_API_KEY": PLACEHOLDER,
        "TAVILY_API_KEY": PLACEHOLDER,
    }

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self.init_file()

    def init_file(self):
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(exist_ok=True, parents=True)

        if not self.file_path.exists():
            self.file_path.touch(exist_ok=True)

        with self.file_path.open("w") as fp:
            toml.dump(self.CONFIG_TEMPLATE, fp)

    @property
    def config(self) -> dict[str, str]:
        if not self.file_path.exists():
            self.init_file()

        with self.file_path.open("r") as fp:
            return toml.load(fp)

    def set(self, config_dict: dict[str, str]):
        origin_config = self.config

        for key, value in config_dict.items():
            if key not in origin_config:
                print(f"Warning: key {key} is not valid config")
                continue

            origin_config[key] = value

        with self.file_path.open("w") as fp:
            toml.dump(origin_config, fp)

    def unset(self, keys: list[str]):
        origin_config = self.config

        for key in keys:
            if key in origin_config:
                origin_config[key] = self.PLACEHOLDER

        with self.file_path.open("w") as fp:
            toml.dump(origin_config, fp)

    def to_env_file(self, env_file_path: str | Path):
        env_file_path = Path(env_file_path)

        if not env_file_path.parent.exists():
            env_file_path.parent.mkdir(parents=True, exist_ok=True)

        env_lines: list[str] = []
        for key, value in self.config.items():
            if value == self.PLACEHOLDER:
                continue

            env_lines.append(f"{key}={value}")

        env_content = "\n".join(env_lines)

        env_file_path.write_text(env_content)


centralized_config = CentralizedConfig(CONFIG_HOME / "config.toml")
