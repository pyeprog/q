from contextlib import suppress
import json
from pathlib import Path
from typing import Literal
from more_itertools import first
from pydantic import BaseModel, Field, TypeAdapter
from pydantic_ai import AbstractToolset, ToolsetFunc

from q.cli.constant import CONFIG_HOME
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio, MCPServerStreamableHTTP


class StdioMCP(BaseModel):
    name: str
    command: str
    args: list[str] = Field(default_factory=list)
    envs: dict[str, str] = Field(default_factory=dict)

    @property
    def toolset(self):
        return MCPServerStdio(command=self.command, args=self.args, env=self.envs)

    @classmethod
    def from_json(cls, json_str: str):
        """load from claude mcp config json

        Args:
            json_str (str): json string in format of
                {
                  "mcpServers": {
                    "youtube": {
                      "command": "npx",
                      "args": ["-y", "zubeid-youtube-mcp-server"],
                      "env": {
                        "YOUTUBE_API_KEY": "your_youtube_api_key_here"
                      }
                    }
                  }
                }

        Returns:
            StdioMCP: object
        """
        config_dict = json.loads(json_str)
        name, config = first(config_dict["mcpServers"].items())
        return cls(name=name, command=config["command"], args=config["args"], envs=config["env"])


class StreamableHttpMCP(BaseModel):
    name: str
    url: str
    type: Literal["http"] = "http"

    @property
    def toolset(self):
        return MCPServerStreamableHTTP(url=self.url)

    @classmethod
    def from_json(cls, json_str: str):
        """load from claude mcp config json

        Args:
            json_str (str): json string in format of
            {
              "mcpServers": {
                "deepwiki": {
                  "serverUrl": "https://mcp.deepwiki.com/mcp"
                }
              }
            }

        Returns:
            StreamableHttpMCP: object
        """
        config_dict = json.loads(json_str)
        name, config = first(config_dict["mcpServers"].items())
        assert "sse" not in config["serverUrl"].lower()
        return cls(name=name, url=config["serverUrl"])


class SSEMCP(BaseModel):
    name: str
    url: str
    type: Literal["sse"] = "sse"

    @property
    def toolset(self):
        return MCPServerSSE(url=self.url)

    @classmethod
    def from_json(cls, json_str: str):
        """load from claude mcp config json

        Args:
            json_str (str): json string in format of
            {
              "mcpServers": {
                "deepwiki": {
                  "serverUrl": "https://mcp.deepwiki.com/sse"
                }
              }
            }

        Returns:
            StreamableHttpMCP: object
        """
        config_dict = json.loads(json_str)
        name, config = first(config_dict["mcpServers"].items())
        return cls(name=name, url=config["serverUrl"])


class MCPManager:
    def __init__(self, dir_path: str | Path) -> None:
        self.dir_path = Path(dir_path)
        if not self.dir_path.exists():
            self.dir_path.mkdir(exist_ok=True, parents=True)

        self.config_file = self.dir_path / "mcp.json"
        if not self.config_file.exists():
            self.config_file.touch(exist_ok=True)
            self.config_file.write_text("[]")

        self.adapter = TypeAdapter(list[StreamableHttpMCP | SSEMCP | StdioMCP])
        self.mcps = self.adapter.validate_json(self.config_file.read_text())

    @property
    def mcp_map(self) -> dict[str, StreamableHttpMCP | SSEMCP | StdioMCP]:
        return {mcp.name: mcp for mcp in self.mcps}

    @property
    def mcp_names(self) -> list[str]:
        return [mcp.name for mcp in self.mcps]

    def get[T](self, mcp_name: str, default: T | None = None, /) -> AbstractToolset | ToolsetFunc | T | None:
        if mcp := self.mcp_map.get(mcp_name):
            return mcp.toolset

        return default

    def add_config_json(self, json_str: str):
        mcp = None
        for mcp_cls in [StdioMCP, StreamableHttpMCP, SSEMCP]:
            with suppress(KeyError, AssertionError):
                mcp = mcp_cls.from_json(json_str)
                break

        if mcp is None:
            raise ValueError(f"invalid mcp config json: {json_str}")

        self.mcps.append(mcp)
        self.config_file.write_bytes(self.adapter.dump_json(self.mcps))

    def rm(self, mcp_name: str):
        self.mcps = [mcp for mcp in self.mcps if mcp.name != mcp_name]
        self.config_file.write_bytes(self.adapter.dump_json(self.mcps))

    def rm_all(self, mcp_names: list[str]):
        for name in mcp_names:
            self.rm(name)


mcp_manager = MCPManager(CONFIG_HOME)
