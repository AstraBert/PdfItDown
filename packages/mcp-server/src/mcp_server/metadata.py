import json
from dataclasses import asdict, dataclass

MCP_SERVER_VERSION = "0.1.0"
MCP_SERVER_NAME = "pdfitdown"
MCP_SERVER_INSTRUCTIONS = """
This MCP server is based on [PdfItDown](https://pdfitdown.eu), a python-native library and CLI tool to convert files to PDF.
This MCP server should be used to convert local files to PDF.
Supported file formats for conversion:
- Markdown
- PowerPoint
- Word
- Excel
- HTML
- Text-based formats (CSV, XML, JSON)
- ZIP files (iterates over contents)
- Image files (PNG, JPG)
"""
TOOL_NAME = "convert-to-pdf"
TOOL_DESCRIPTION = """
Converts one or more files to PDF.
Supported formats:
- Markdown
- PowerPoint
- Word
- Excel
- HTML
- Text-based formats (CSV, XML, JSON)
- ZIP files (iterates over contents)
- Image files (PNG, JPG)

The tool receives, as input, a list of files to convert and return, as output, a list of path for the converted files.
It can optionally be specified whether or not files should be overwritten (by default, they are overwritten).
The tool returns the list of file paths to which the converted files have been saved.
The output paths are provided in the same order as the input paths.
"""


@dataclass
class ToolMetadata:
    tool_name: str
    tool_description: str

    def to_pretty(self) -> str:
        return f"**{self.tool_name}**\n\n{self.tool_description}"


@dataclass
class McpServerMetadata:
    mcp_server_name: str
    mcp_server_instructions: str
    mcp_server_version: str
    tools: list[ToolMetadata]

    def to_pretty(self) -> str:
        return f"""
## MCP Server Details

**Name**

{self.mcp_server_name}

**Instructions**

{self.mcp_server_instructions}

**Version**

{self.mcp_server_version}

## Tools
{self._pretty_tools()}
"""

    def _pretty_tools(self) -> str:
        return "\n\n---\n\n".join([tool.to_pretty() for tool in self.tools])


def get_metadata(pretty: bool) -> str:
    meta = McpServerMetadata(
        mcp_server_name=MCP_SERVER_NAME,
        mcp_server_version=MCP_SERVER_VERSION,
        mcp_server_instructions=MCP_SERVER_INSTRUCTIONS,
        tools=[ToolMetadata(tool_name=TOOL_NAME, tool_description=TOOL_DESCRIPTION)],
    )
    if pretty:
        return meta.to_pretty()
    return json.dumps(asdict(meta), indent=2)
