# pdfitdown-mcp-server

PdfItDown MCP server is built on top of [FastMCP](https://gofastmcp.com/getting-started/welcome) and runs over `stdio` transport.

Install the server with:

```bash
# uv
uv tool install pdfitdown-mcp-server
# pip
pip install pdfitdown-mcp-server
```

You can run the server with:

```bash
pdfitdown-mcp run
```

Here are the options for the `run` command:

- `--show-banner`/`--no-show-banner`: show the FastMCP banner on startup (defaults to false)
- `--log-level`: set a log level for the MCP server (defaults to unset)

You can take a look at details about the server itself with:

```bash
# print as markdown (default)
pdfitdown-mcp metadata
# print as JSON
pdfitdown-mcp metadata --no-pretty
```

See the full MCP server spec [on the dedicate page](https://pdfitdown.eu/api-reference/mcp-server)
