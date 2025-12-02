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
