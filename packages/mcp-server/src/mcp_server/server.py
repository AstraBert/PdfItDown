import asyncio

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from pdfitdown.pdfconversion import Converter

from .metadata import (
    MCP_SERVER_INSTRUCTIONS,
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    TOOL_DESCRIPTION,
    TOOL_NAME,
)

converter = Converter()
mcp = FastMCP(
    name=MCP_SERVER_NAME,
    version=MCP_SERVER_VERSION,
    instructions=MCP_SERVER_INSTRUCTIONS,
)


@mcp.tool(
    name=TOOL_NAME,
    description=TOOL_DESCRIPTION,
)
def convert_to_pdf(files: list[str], overwrite: bool = True) -> ToolResult:
    output_paths = converter.multiple_convert(files, overwrite=overwrite)
    content = [TextContent(type="text", text=path) for path in output_paths]
    return ToolResult(content=content)


def run_mcp(log_level: str | None = None, show_banner: bool = False) -> None:
    asyncio.run(mcp.run_stdio_async(log_level=log_level, show_banner=show_banner))
