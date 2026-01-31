from typing import Annotated

from rich import print as rprint
from rich import print_json
from rich.markdown import Markdown
from typer import Option, Typer

from .metadata import get_metadata
from .server import run_mcp

app = Typer()


@app.command(name="run", help="Run the stdio MCP server")
def run(
    show_banner: Annotated[
        bool,
        Option(
            help="Whether or not to show the FastMCP server banner. Defaults to false",
            is_flag=True,
        ),
    ] = False,
    log_level: Annotated[
        str | None, Option(help="Log level for the MCP server")
    ] = None,
) -> None:
    run_mcp(show_banner=show_banner, log_level=log_level)


@app.command(name="metadata", help="Get the metadata of the MCP server")
def get_server_metadata(
    pretty: Annotated[
        bool,
        Option(
            help="Whether to render metadata as markdown text (`--pretty`) or as JSON (`--no-pretty`)",
            is_flag=True,
        ),
    ] = True,
) -> None:
    meta = get_metadata(pretty=pretty)
    if pretty:
        rprint(Markdown(meta))
    else:
        print_json(meta)
