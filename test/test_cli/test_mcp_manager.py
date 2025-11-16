import json
from pathlib import Path
import shutil
import tempfile
from typing import Generator

import pytest
from q.cli.manager.mcp import SSEMCP, MCPManager, StreamableHttpMCP


@pytest.fixture
def mcp_manager() -> Generator[MCPManager, None, None]:
    dir_path = Path(tempfile.gettempdir()) / "mcpdir"
    if dir_path.exists():
        shutil.rmtree(dir_path)

    dir_path.mkdir(exist_ok=True, parents=True)
    mcp_manager = MCPManager(dir_path)
    json_str = '{"name": "bilibili", "url": "www.bilibili.com/mcp", "type": "http"}'
    mcp_manager.config_file.write_text(json_str)
    yield mcp_manager

    shutil.rmtree(dir_path)


def test_add_get_and_remove_stdio_mcp(mcp_manager):
    mgr = mcp_manager

    stdio_json = json.dumps(
        {
            "mcpServers": {
                "youtube": {
                    "command": "npx",
                    "args": ["-y", "zubeid-youtube-mcp-server"],
                    "env": {"YOUTUBE_API_KEY": "key"},
                }
            }
        }
    )

    mgr.add_config_json(stdio_json)
    assert "youtube" in mgr.mcp_names

    m = mgr.get("youtube")
    assert m.name == "youtube"
    assert getattr(m, "command", None) == "npx"
    assert m.args == ["-y", "zubeid-youtube-mcp-server"]
    assert m.envs["YOUTUBE_API_KEY"] == "key"

    # persisted to disk
    mgr2 = MCPManager(mgr.dir_path)
    assert "youtube" in mgr2.mcp_names

    mgr.rm("youtube")
    assert "youtube" not in mgr.mcp_names
    mgr3 = MCPManager(mgr.dir_path)
    assert "youtube" not in mgr3.mcp_names


def test_add_streamable_and_sse(mcp_manager):
    mgr = mcp_manager

    stream_json = json.dumps({"mcpServers": {"deepwiki": {"url": "https://mcp.deepwiki.com/mcp"}}})
    sse_json = json.dumps({"mcpServers": {"sse_server": {"url": "https://mcp.example.com/sse"}}})

    mgr.add_config_json(stream_json)
    assert "deepwiki" in mgr.mcp_names
    deep = mgr.get("deepwiki")
    assert isinstance(deep, StreamableHttpMCP)
    assert getattr(deep, "url", "").startswith("https://")

    mgr.add_config_json(sse_json)
    assert "sse_server" in mgr.mcp_names
    sse = mgr.get("sse_server")
    assert isinstance(sse, SSEMCP)
    assert sse.url.endswith("/sse")
