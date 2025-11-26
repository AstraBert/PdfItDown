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
