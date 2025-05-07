import warnings
import os
try:
    from .pdfconversion import Converter
except ImportError:
    from pdfconversion import Converter
from typing import List
import gradio as gr

class FileNotConvertedWarning(Warning):
    """The file was not in one of the specified formats for conversion to PDF,thus it was not converted"""

def to_pdf(files: List[str]) -> List[str]:
    pdfs = []
    converter = Converter()
    for fl in files:
        try:
            outf = converter.convert(fl, fl.replace(os.path.splitext(fl)[1], ".pdf"))
        except Exception as e:
            warnings.warn(f"File {fl} not converted because of an error during the conversion: {e}", FileNotConvertedWarning)
        else:
            pdfs.append(outf)
    return pdfs

def convert_files(files: List[str]) -> List[str]:
    pdfs = to_pdf(files)
    return pdfs

def main():
    iface = gr.Interface(
        fn=convert_files,
        inputs=gr.File(label="Upload your file", file_count="multiple"),
        outputs=gr.File(label="Converted PDF", file_count="multiple"),
        title="File to PDF Converter",
        description="Upload a file in .docx, .xlsx, .html, .pptx, .json, .csv, .xml, .md, .jpg/.jpeg, .png, .zip format, and get it converted to PDF."
    )
    iface.launch()

if __name__ == "__main__":
    main()
