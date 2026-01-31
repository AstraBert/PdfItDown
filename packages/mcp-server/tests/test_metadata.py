import json
from dataclasses import asdict

from mcp_server.metadata import (
    MCP_SERVER_INSTRUCTIONS,
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    TOOL_DESCRIPTION,
    TOOL_NAME,
    McpServerMetadata,
    ToolMetadata,
    get_metadata,
)


def test_tool_metadata_to_pretty() -> None:
    tool_metadata = ToolMetadata(tool_name="name", tool_description="description")
    assert tool_metadata.to_pretty() == "**name**\n\ndescription"


def test_mcp_server_metadata_to_pretty() -> None:
    tools = [
        ToolMetadata(tool_name="name", tool_description="description"),
        ToolMetadata(tool_name="name1", tool_description="description1"),
    ]
    server_meta = McpServerMetadata(
        mcp_server_name="server",
        mcp_server_instructions="instructions here",
        mcp_server_version="0.1.0",
        tools=tools,
    )
    assert (
        server_meta.to_pretty()
        == "\n## MCP Server Details\n\n**Name**\n\nserver\n\n**Instructions**\n\ninstructions here\n\n**Version**\n\n0.1.0\n\n## Tools\n**name**\n\ndescription\n\n---\n\n**name1**\n\ndescription1\n"
    )


def test_get_metadata() -> None:
    meta = McpServerMetadata(
        mcp_server_name=MCP_SERVER_NAME,
        mcp_server_version=MCP_SERVER_VERSION,
        mcp_server_instructions=MCP_SERVER_INSTRUCTIONS,
        tools=[ToolMetadata(tool_name=TOOL_NAME, tool_description=TOOL_DESCRIPTION)],
    )
    assert get_metadata(True) == meta.to_pretty()
    assert get_metadata(False) == json.dumps(asdict(meta), indent=2)
