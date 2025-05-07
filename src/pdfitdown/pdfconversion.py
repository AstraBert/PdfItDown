import img2pdf
import warnings
import os
from PIL import Image
from markdown_pdf import MarkdownPdf, Section
from pydantic import BaseModel, field_validator, model_validator
from pathlib import Path
from typing import List, Optional
from typing_extensions import Self
from llama_index.core.readers.base import BaseReader
from llama_index.readers.markitdown import MarkItDownReader

class FilePath(BaseModel):
    file: str
    @field_validator("file")
    def is_valid_file(cls, file: str):
        p = Path(file)
        if not p.is_file():
            raise ValueError(f"{file} is not a file")
        return file

class FileExistsWarning(Warning):
    """Warns you that a file exists"""

class DirPath(BaseModel):
    path: str
    @model_validator(mode="after")
    def validate_dir_path(self) -> Self:
        if Path(self.path).is_dir():
            if len(os.listdir(self.path)) == 0:
                raise ValueError("You should provide a non-empty directory")
            else:
                return self
        else:
            raise ValueError("You should provide the path for an existing directory")

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

class MultipleFileConversion(BaseModel):
    input_files: List[FilePath]
    output_files: List[str] | List[OutputPath] | None
    @model_validator(mode="after")
    def validate_multiple_file_conversion(self) -> Self:
        if self.output_files is not None and len(self.input_files) != len(self.output_files):
            raise ValueError("Input and output files must be lists of the same length")
        else:
            if self.output_files is None:
                self.output_files = [OutputPath(file=(fl.file.replace(os.path.splitext(fl.file)[1],".pdf"))) for fl in self.input_files]
            else:
                if isinstance(self.output_files[0], str):
                    self.output_files = [OutputPath(file=fl) for fl in self.output_files]
        return self

class Converter:
    """A class for converting .docx, .html, .xml, .json, .csv, .md, .pptx, .xlsx, .png, .jpg, .png, .zip files into PDF"""
    def __init__(self, reader: Optional[BaseReader] = None) -> None:
        """
        Initialize the Converter class.

        Args:
            reader (Optional[BaseReader]): the reader to extract the file text (needs to be LlamaIndex-compatible). Defaults to MarkItDown reader.
        Returns:
            None
        """
        if reader is not None:
            self._reader = reader
        else:
            self._reader = MarkItDownReader()
        return
    def convert(self,  file_path: str, output_path: str, title: str = "File Converted with PdfItDown"):
        """
        Convert various document types into PDF format (supports .docx, .html, .xml, .json, .csv, .md, .pptx, .xlsx, .png, .jpg, .png, .zip).

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
            try:
                result = self._reader.load_data([self.file_input.file])
                finstr = result[0].text
                pdf = MarkdownPdf(toc_level=0)
                pdf.add_section(Section(finstr))
                pdf.meta["title"] = title
                pdf.save(self.file_output.file)
                return self.file_output.file
            except Exception:
                return None
    def multiple_convert(self,  file_paths: List[str], output_paths: Optional[List[str]] = None):
        """
        Convert various document types into PDF format (supports .docx, .html, .xml, .json, .csv, .md, .pptx, .xlsx, .png, .jpg, .png, .zip). Converts multiple files at once.

        Args:
            file_paths (str): The paths to the input files
            output_paths (Optional[str]): The path to the output files
        Returns:
            output_paths (List[str]): Paths to the output files
        Raises:
            ValidationError: if the format of the input file is not support or if the format of the output file is not PDF
            FileExistsWarning: if the output PDF path is an existing file, it warns you that the file will be overwritten
        """
        for file in file_paths:
            input_files = [FilePath(file=fl) for fl in file_paths]
            to_convert_list = MultipleFileConversion(input_files=input_files, output_files=output_paths)
            for i in range(len(to_convert_list.input_files)):
                result = self.convert(file_path=to_convert_list.input_files[i].file, output_path=to_convert_list.output_files[i].file)
                if result is None:
                    to_convert_list.output_files.remove(to_convert_list.output_files[i])
            return [el.file for el in to_convert_list.output_files]
    def convert_directory(self, directory_path: str):
        """
        Convert various document types into PDF format (supports .docx, .html, .xml, .json, .csv, .md, .pptx, .xlsx, .png, .jpg, .png, .zip). Converts all the files in a directory at once.

        Args:
            directory_path (str): The paths to the input files
        Returns:
            output_paths (List[str]): Paths to the output files
        Raises:
            ValidationError: if the format of the input file is not support or if the format of the output file is not PDF
            FileExistsWarning: if the output PDF path is an existing file, it warns you that the file will be overwritten
        """
        dirpath = DirPath(path=directory_path)
        fls = []
        p = os.walk(dirpath.path)
        for root, parent, file in p:
            for f in file:
                fls.append(root+"/"+f)
        output_paths = self.multiple_convert(file_paths=fls)
        return output_paths
