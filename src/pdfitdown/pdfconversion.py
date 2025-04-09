from markitdown import MarkItDown
from PIL import Image
import img2pdf
from markdown_pdf import MarkdownPdf, Section
import os
from pydantic import BaseModel, field_validator
from pathlib import Path
import warnings

class FilePath(BaseModel):
    file: str
    @field_validator("file")
    def is_valid_file(cls, file: str):
        p = Path(file)
        if not p.is_file():
            raise ValueError(f"{file} is not a file")
        else:
            if os.path.splitext(file)[1] not in [".docx", ".html", ".xml", ".csv", ".md", ".pptx", ".xlsx", ".png", ".jpg", ".png"]:
                raise ValueError(f"File format for {file} not supported, please provide a file that has one of the following formats:\n\n- "+"\n- ".join([".docx", ".html", ".xml", ".csv", ".md", ".pptx", ".xlsx", ".png", ".jpg", ".png"]))
            return file

class FileExistsWarning(Warning):
    """Warns you that a file exists"""

class OutputPath(BaseModel):
    file: str
    @field_validator("file")
    def file_exists_warning(cls, file: str):
        if os.path.splitext(file)[1] != ".pdf":
            raise ValueError("Output file must be a PDF")
        p = Path(file)
        if p.is_file():
            warnings.warn(f"The file {file} already exists, you are about to overwrite it", FileExistsWarning)
        return file

class Converter:
    """A class for converting .docx, .html, .xml, .csv, .md, .pptx, .xlsx, .png, .jpg, .png files into PDF"""
    def __init__(self) -> None:
        """
        Initialize the Converter class.
        
        Args:
            None
        Returns:
            None
        """
        return
    def convert(self,  file_path: str, output_path: str, title: str = "File Converted with PdfItDown"):
        """
        Convert various document types into PDF format (supports .docx, .html, .xml, .csv, .md, .pptx, .xlsx, .png, .jpg, .png). 
        
        Args:
            file_path (str): The path to the input file
            output_path (str): The path to the output file
            title (str): The title for the PDF document (defaults to: 'File Converted with PdfItDown')
        Returns:
            output_path (str): Path to the output file
        Raises:
            ValidationError: if the format of the input file is not support or if the format of the output file is not PDF
            FileExistsWarning: if the output PDF path is an existing file, it warns you that the file will be overwritten
        """
        self.file_input = FilePath(file=file_path)
        self.file_output = OutputPath(file=output_path)
        if os.path.splitext(self.file_input.file)[1] == ".md":
            f = open(self.file_input.file, "r")
            finstr = f.read()     
            f.close()       
            pdf = MarkdownPdf(toc_level=0)
            pdf.add_section(Section(finstr))
            pdf.meta["title"] = title
            pdf.save(self.file_output.file)
            return self.file_output.file
        elif os.path.splitext(self.file_input.file)[1] in [".jpg", ".png"]:
            image = Image.open(self.file_input.file)
            pdf_bytes = img2pdf.convert(image.filename)
            with open(self.file_output.file, "wb") as file:
                file.write(pdf_bytes)
            file.close()
            image.close()
            return self.file_output.file
        else:
            md = MarkItDown()
            result = md.convert(self.file_input.file)
            finstr = result.text_content
            pdf = MarkdownPdf(toc_level=0)
            pdf.add_section(Section(finstr))
            pdf.meta["title"] = title
            pdf.save(self.file_output.file)
            return self.file_output.file
