from markitdown import MarkItDown
from markdown_pdf import MarkdownPdf, Section
from PIL import Image
from img2pdf import convert as image_to_pdf
from typing import cast
from .models import OsPath
from .errors import EmptyImageError

CONVERTER = MarkItDown(enable_builtins=True)


def convert_file(
    input_file: str, output_fle: str, title: str | None = None, overwrite: bool = False
) -> str | None:
    """
    Converts an input file to a PDF file, supporting image, PDF, text, and convertible file types.

    Args:
        input_file (str): Path to the input file to be converted.
        output_fle (str): Path where the output PDF file will be saved.
        title (str | None): Title for the PDF document. If None, a default title is used.
        overwrite (bool): Whether to overwrite the output file if it exists. Defaults to False.

    Returns:
        str | None: The path to the output PDF file if conversion is successful, otherwise None.

    Raises:
        EmptyImageError: If the input image file is empty or cannot be read.
    """
    title = title or f"{input_file} - Converted with PdfItDown"
    inpt = OsPath.from_file(input_file, overwrite=overwrite, is_input=True)
    outpt = OsPath.from_file(output_fle, overwrite=overwrite, is_input=False)
    if inpt.file_type == "image":
        image = Image.open(input_file)
        content = image_to_pdf(image.filename)
        if content is not None:
            outpt.write_file(content=content)
        else:
            raise EmptyImageError(
                f"{input_file} appears to be empty or could not be read."
            )
        return output_fle
    elif inpt.file_type == "pdf":
        content = cast(bytes, inpt.read_file())
        outpt.write_file(content=content)
        return output_fle
    elif inpt.file_type == "text":
        content = cast(str, inpt.read_file())
        pdf = MarkdownPdf(toc_level=0)
        pdf.add_section(Section(content))
        pdf.meta["title"] = title
        pdf.save(outpt.path)
        return output_fle
    elif inpt.file_type == "toconvert":
        result = CONVERTER.convert(inpt.path)
        pdf = MarkdownPdf(toc_level=0)
        pdf.add_section(Section(result.markdown))
        pdf.meta["title"] = title
        pdf.save(outpt.path)
        return output_fle
    else:
        return None
