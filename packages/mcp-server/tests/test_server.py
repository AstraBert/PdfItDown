from pathlib import Path

import pytest
from fastmcp.client.client import Client
from fastmcp.exceptions import ToolError
from mcp.types import TextContent

from mcp_server.metadata import TOOL_NAME
from mcp_server.server import mcp


def prepare_tmp_path(tmp_path: Path) -> list[str]:
    (tmp_path / "hello.txt").write_text("This is a test file")
    (tmp_path / "test.md").write_text("This is a test markdown file")
    return [str(tmp_path / "hello.txt"), str(tmp_path / "test.md")]


@pytest.mark.asyncio
async def test_mcp_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    files = prepare_tmp_path(tmp_path)
    async with Client(mcp) as client:
        result = await client.call_tool(name=TOOL_NAME, arguments={"files": files})
        assert not result.is_error
        assert len(result.content) == 2
        file_1 = result.content[0]
        file_2 = result.content[1]
        assert isinstance(file_1, TextContent)
        assert file_1.text == files[0].replace(".txt", ".pdf")
        assert isinstance(file_2, TextContent)
        assert file_2.text == files[1].replace(".md", ".pdf")


@pytest.mark.asyncio
async def test_mcp_server_overwrite_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    files = prepare_tmp_path(tmp_path)
    async with Client(mcp) as client:
        result = await client.call_tool(name=TOOL_NAME, arguments={"files": files})
        assert not result.is_error
        with pytest.raises(
            ToolError,
            match=r"File .* already exists\. If you wish to overwrite, please set `overwrite` to True",
        ):
            await client.call_tool(
                name=TOOL_NAME, arguments={"files": files, "overwrite": False}
            )


@pytest.mark.asyncio
async def test_mcp_server_notexist_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    files = prepare_tmp_path(tmp_path)
    files[0] = files[0].replace(".txt", ".xml")
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match=r"No such file:\s.*"):
            await client.call_tool(name=TOOL_NAME, arguments={"files": files})
