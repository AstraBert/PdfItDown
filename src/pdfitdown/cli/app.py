import click
from pathlib import Path
from click.exceptions import Exit
from termcolor import cprint
from typing import cast
from ..pdfconversion.converter import Converter


@click.command(
    help="Convert (almost) everything to PDF",
)
@click.option(
    "-i",
    "--inputfile",
    help="Path to the input file(s) that need to be converted to PDF. Can be used multiple times.",
    required=False,
    default=None,
    multiple=True,
)
@click.option(
    "-o",
    "--outputfile",
    help="Path to the output PDF file(s). If more than one input file is provided, you should provide an equal number of output files.",
    required=False,
    default=None,
    multiple=True,
)
@click.option(
    "-t",
    "--title",
    help="Title to include in the PDF metadata. Default: 'File Converted with PdfItDown'. If more than one file is provided, it will be ignored.",
    required=False,
    default=None,
)
@click.option(
    "-d",
    "--directory",
    help="Directory whose files you want to bulk-convert to PDF. If `--inputfile` is also provided, this option will be ignored. Defaults to None.",
    required=False,
    default=None,
)
def pdfitdown_cli(
    inputfile: tuple[str, ...] | None,
    outputfile: tuple[str, ...] | None,
    title: str | None,
    directory: str | None,
):
    c = Converter()
    if (
        inputfile is None or (inputfile is not None and len(inputfile) == 0)
    ) and directory is None:
        cprint(
            "ERROR! You should provide one of `--inputfile` or `--directory`",
            attrs=["bold"],
            color="red",
        )
        raise Exit(1)
    elif inputfile is not None and len(inputfile) > 0:
        if directory is not None:
            cprint(
                "WARNING: `--directory` will be ignored since `--inputfile` has been provided",
                attrs=["bold"],
                color="yellow",
            )
        if len(inputfile) == 1:
            if outputfile is None or len(outputfile) == 0:
                outputfile = (inputfile[0].replace(Path(inputfile[0]).suffix, ".pdf"),)
            try:
                c.convert(inputfile[0], outputfile[0], title, True)
            except Exception as e:
                cprint(
                    f"ERROR during the conversion: {e}",
                    attrs=["bold"],
                    color="red",
                )
                raise Exit(2)
            cprint(
                "Conversion successful!🎉",
                color="green",
                attrs=["bold"],
            )
        else:
            if title is not None:
                cprint(
                    "WARNING: `--title` will be ignored since more than one `--inputfile` has been provided",
                    attrs=["bold"],
                    color="yellow",
                )
            outputfile_ls = None
            if outputfile is not None and len(outputfile) > 0:
                outputfile_ls = list(outputfile)
            if outputfile_ls is not None and len(outputfile_ls) != len(inputfile):
                cprint(
                    "ERROR! `--inputfile` and `--outputfile` should be the same number",
                    attrs=["bold"],
                    color="red",
                )
                raise Exit(1)
            try:
                c.multiple_convert(list(inputfile), outputfile_ls)
            except Exception as e:
                cprint(
                    f"ERROR during the conversion: {e}",
                    attrs=["bold"],
                    color="red",
                )
                raise Exit(2)
            cprint(
                "Conversion successful!🎉",
                color="green",
                attrs=["bold"],
            )
    else:
        directory = cast(str, directory)
        if outputfile is not None and len(outputfile) > 0:
            cprint(
                "WARNING: `--outputfile` will be ignored since  `--inputfile` has not been provided",
                attrs=["bold"],
                color="yellow",
            )
        if title is not None:
            cprint(
                "WARNING: `--title` will be ignored since `--directory` has been provided",
                attrs=["bold"],
                color="yellow",
            )
        try:
            c.convert_directory(directory)
        except Exception as e:
            cprint(
                f"ERROR during the conversion: {e}",
                attrs=["bold"],
                color="red",
            )
            raise Exit(2)
        cprint(
            "Conversion successful!🎉",
            color="green",
            attrs=["bold"],
        )
