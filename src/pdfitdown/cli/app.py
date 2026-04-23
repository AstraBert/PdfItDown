import subprocess
import sys
from typer import Typer, Option, Exit
from typing import Annotated, cast
from rich import print as rprint
from pathlib import Path
from ..pdfconversion.converter import Converter

app = Typer()


@app.command()
def main(
    inputfile: Annotated[
        list[str],
        Option(
            "--inputfile",
            "-i",
            help="Path to the input file(s) that need to be converted to PDF. Can be used multiple times.",
        ),
    ] = [],
    outputfile: Annotated[
        list[str],
        Option(
            "--outputfile",
            "-o",
            help="Path to the output PDF file(s). If more than one input file is provided, you should provide an equal number of output files.",
        ),
    ] = [],
    title: Annotated[
        str | None,
        Option(
            "-t",
            "--title",
            help="Title to include in the PDF metadata. Default: 'File Converted with PdfItDown'. If more than one file is provided, it will be ignored.",
        ),
    ] = None,
    directory: Annotated[
        str | None,
        Option(
            "-d",
            "--directory",
            help="Directory whose files you want to bulk-convert to PDF. If `--inputfile` is also provided, this option will be ignored. Defaults to None.",
        ),
    ] = None,
):
    c = Converter()
    if len(inputfile) == 0 and directory is None:
        rprint(
            "[bold red]ERROR! You should provide one of `--inputfile` or `--directory`[/]",
        )
        raise Exit(1)
    elif len(inputfile) > 0:
        if directory is not None:
            rprint(
                "[bold yellow]WARNING: `--directory` will be ignored since `--inputfile` has been provided[/]",
            )
        if len(inputfile) == 1:
            if len(outputfile) == 0:
                outputfile = [inputfile[0].replace(Path(inputfile[0]).suffix, ".pdf")]
            try:
                c.convert(inputfile[0], outputfile[0], title, True)
            except Exception as e:
                rprint(
                    f"[bold red]ERROR during the conversion: {e}[/]",
                )
                raise Exit(2)
            rprint(
                "[bold green]Conversion successful![/]🎉",
            )
        else:
            if title is not None:
                rprint(
                    "[bold yellow]WARNING: `--title` will be ignored since more than one `--inputfile` has been provided[/]",
                )
            outputfile_ls = None
            if len(outputfile) > 0:
                outputfile_ls = outputfile
            if outputfile_ls is not None and len(outputfile_ls) != len(inputfile):
                rprint(
                    "[bold red]ERROR! `--inputfile` and `--outputfile` should be the same number[/]",
                )
                raise Exit(1)
            try:
                c.multiple_convert(list(inputfile), outputfile_ls)
            except Exception as e:
                rprint(
                    f"[bold red]ERROR during the conversion: {e}[/]",
                )
                raise Exit(2)
            rprint(
                "Conversion successful!🎉",
            )
    else:
        directory = cast(str, directory)
        if len(outputfile) > 0:
            rprint(
                "[bold yellow]WARNING: `--outputfile` will be ignored since  `--inputfile` has not been provided[/]",
            )
        if title is not None:
            rprint(
                "[bold yellow]WARNING: `--title` will be ignored since `--directory` has been provided[/]",
            )
        try:
            c.convert_directory(directory)
        except Exception as e:
            rprint(
                f"[bold red]ERROR during the conversion: {e}",
            )
            raise Exit(2)
        rprint(
            "[bold green]Conversion successful![/]🎉",
        )


@app.command()
def web(
    host: Annotated[
        str,
        Option(
            "--host",
            "-H",
            help="绑定的主机地址 (默认: 0.0.0.0)",
        ),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        Option(
            "--port",
            "-p",
            help="服务端口 (默认: 8000)",
        ),
    ] = 8000,
    reload: Annotated[
        bool,
        Option(
            "--reload",
            "-r",
            help="启用自动重载模式 (开发模式)",
        ),
    ] = False,
):
    """
    启动 Web 可视化转换服务
    """
    try:
        import uvicorn
        from pdfitdown.web.app import app as web_app
    except ImportError as e:
        rprint(f"[bold red]ERROR: 缺少 Web 服务依赖: {e}[/]")
        rprint("[bold yellow]请运行: pip install pdfitdown[web][/]")
        raise Exit(1)
    
    rprint("=" * 60)
    rprint("[bold cyan]  PdfItDown Web - 文件转PDF在线转换服务[/]")
    rprint("=" * 60)
    rprint(f"  服务地址: http://{host}:{port}")
    rprint(f"  本地访问: http://localhost:{port}")
    rprint("=" * 60)
    rprint()
    rprint("[bold green]请在浏览器中打开上述地址开始使用。[/]")
    rprint("[bold yellow]按 Ctrl+C 停止服务。[/]")
    rprint()
    
    uvicorn.run(
        "pdfitdown.web.app:app",
        host=host,
        port=port,
        reload=reload,
    )
