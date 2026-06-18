try:
    from markitdown import MarkItDown  # pyright: ignore[reportUnknownVariableType]

    HAS_MARKITDOWN = True
except ImportError:
    HAS_MARKITDOWN = False
import os
from typing import cast

from img2pdf import (
    convert as image_to_pdf,  # pyright: ignore[reportUnknownVariableType]
)
from liteparse import LiteParse
from markdown_pdf import MarkdownPdf, Section
from PIL import Image

from .errors import EmptyImageError
from .models import OsPath

if HAS_MARKITDOWN:
    CONVERTER = MarkItDown(enable_builtins=True)  # pyright: ignore[reportPossiblyUnboundVariable, reportUnknownVariableType]

    def convert_file(
        input_file: str,
        output_file: str,
        title: str | None = None,
        overwrite: bool = False,
    ) -> str | None:
        """
        Converts an input file to a PDF file, supporting image, PDF, text, and convertible file types.

        Args:
            input_file (str): Path to the input file to be converted.
            output_file (str): Path where the output PDF file will be saved.
            title (str | None): Title for the PDF document. If None, a default title is used.
            overwrite (bool): Whether to overwrite the output file if it exists. Defaults to False.

        Returns:
            str | None: The path to the output PDF file if conversion is successful, otherwise None.

        Raises:
            EmptyImageError: If the input image file is empty or cannot be read.
        """
        title = title or f"{input_file} - Converted with PdfItDown"
        inpt = OsPath.from_file(input_file, overwrite=overwrite, is_input=True)
        outpt = OsPath.from_file(output_file, overwrite=overwrite, is_input=False)
        if inpt.file_type == "image":
            image = Image.open(input_file)
            content = image_to_pdf(image.filename)
            if content is not None:
                outpt.write_file(content=content)
            else:
                raise EmptyImageError(
                    f"{input_file} appears to be empty or could not be read."
                )
            return output_file
        elif inpt.file_type == "pdf":
            content = cast(bytes, inpt.read_file())
            outpt.write_file(content=content)
            return output_file
        elif inpt.file_type == "text":
            content = cast(str, inpt.read_file())
            pdf = MarkdownPdf(toc_level=0)
            _ = pdf.add_section(Section(content))
            pdf.meta["title"] = title
            pdf.save(outpt.path)
            return output_file
        elif inpt.file_type == "toconvert" or inpt.file_type == "zip":
            result = cast(MarkItDown, CONVERTER).convert(inpt.path)  # pyright: ignore[reportPossiblyUnboundVariable, reportUnknownMemberType, reportUnknownVariableType]
            pdf = MarkdownPdf(toc_level=0)
            _ = pdf.add_section(Section(result.markdown))  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            pdf.meta["title"] = title
            pdf.save(outpt.path)
            return output_file
        else:
            return None
else:
    from tempfile import TemporaryDirectory
    from zipfile import ZipFile

    CONVERTER = LiteParse(output_format="markdown", quiet=True)

    def convert_file(
        input_file: str,
        output_file: str,
        title: str | None = None,
        overwrite: bool = False,
    ) -> str | None:
        """
        Converts an input file to a PDF file, supporting image, PDF, text, and convertible file types.

        Args:
            input_file (str): Path to the input file to be converted.
            output_file (str): Path where the output PDF file will be saved.
            title (str | None): Title for the PDF document. If None, a default title is used.
            overwrite (bool): Whether to overwrite the output file if it exists. Defaults to False.

        Returns:
            str | None: The path to the output PDF file if conversion is successful, otherwise None.

        Raises:
            EmptyImageError: If the input image file is empty or cannot be read.
            ParseError: LiteParse-specific error for unsupported files
        """
        title = title or f"{input_file} - Converted with PdfItDown"
        inpt = OsPath.from_file(input_file, overwrite=overwrite, is_input=True)
        outpt = OsPath.from_file(output_file, overwrite=overwrite, is_input=False)
        if inpt.file_type == "image":
            image = Image.open(input_file)
            content = image_to_pdf(image.filename)
            if content is not None:
                outpt.write_file(content=content)
            else:
                raise EmptyImageError(
                    f"{input_file} appears to be empty or could not be read."
                )
            return output_file
        elif inpt.file_type == "pdf":
            content = cast(bytes, inpt.read_file())
            outpt.write_file(content=content)
            return output_file
        elif inpt.file_type == "text":
            content = cast(str, inpt.read_file())
            pdf = MarkdownPdf(toc_level=0)
            _ = pdf.add_section(Section(content))
            pdf.meta["title"] = title
            pdf.save(outpt.path)
            return output_file
        elif inpt.file_type == "toconvert":
            result = cast(LiteParse, CONVERTER).parse(inpt.path)
            pdf = MarkdownPdf(toc_level=0)
            _ = pdf.add_section(Section(result.text))
            pdf.meta["title"] = title
            pdf.save(outpt.path)
            return output_file
        elif inpt.file_type == "zip":
            with TemporaryDirectory(prefix="pdfitdown-convert-") as tmp_dir:
                with ZipFile(inpt.path) as zf:
                    zf.extractall(tmp_dir)
                files = [
                    os.path.join(root, f)
                    for root, _, filenames in os.walk(tmp_dir)
                    for f in filenames
                ]
                texts: list[str] = []
                for f in files:
                    ospath = OsPath.from_file(f, overwrite, is_input=True)
                    if ospath.file_type == "text":
                        parsed = cast(str, ospath.read_file())
                    elif (
                        ospath.file_type == "pdf"
                        or ospath.file_type == "toconvert"
                        or ospath.file_type == "image"
                    ):
                        parsed = (cast(LiteParse, CONVERTER).parse(f)).text
                    else:
                        continue

                    texts.append(os.path.relpath(f, tmp_dir) + "\n\n" + parsed)  # ty: ignore[invalid-argument-type]
                pdf = MarkdownPdf(toc_level=0)
                _ = pdf.add_section(Section("\n\n---\n\n".join(texts)))
                pdf.meta["title"] = title
                pdf.save(outpt.path)
                return output_file
        else:
            return None
