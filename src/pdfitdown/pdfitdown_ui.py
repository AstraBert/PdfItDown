try:
    from .pdfconversion import convert_to_pdf, convert_markdown_to_pdf, convert_image_to_pdf
except ImportError:
    from pdfconversion import convert_to_pdf, convert_markdown_to_pdf, convert_image_to_pdf
import warnings
from typing import List
import gradio as gr

class FileNotConvertedWarning(Warning):
    """The file was not in one of the specified formats for conversion to PDF,thus it was not converted"""

def to_pdf(files: List[str]) -> List[str]:
    """
    Converts various file formats to PDF.
    
    Args:
        files: List of file paths to convert. Supports .docx, .pdf, .html, .pptx, 
              .csv, .xml, and .md files.
    
    Returns:
        List of paths to converted PDF files. For files already in PDF format, 
        returns original path.
    
    Raises:
        FileNotConvertedWarning: When file format is not supported.
    """
    pdfs = []
    for f in files:
        if not f.endswith(".md"):
            if not (f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png")):
                extension = f.split(".")[-1]
                newfile = f.replace("."+extension, ".pdf")
                file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
                pdfs.append(file_to_add)
            else:
                extension = f.split(".")[-1]
                newfile = f.replace("."+extension, ".pdf")
                file_to_add = convert_image_to_pdf(f, newfile)
                pdfs.append(file_to_add)
        elif f.endswith(".md"):
            newfile = f.replace(".md", ".pdf")
            file_to_add = convert_markdown_to_pdf(f, newfile, newfile.split(".")[0])
            pdfs.append(file_to_add)
        else:
            warnings.warn(f"File {f} was not converted to PDF because its file format is not included in those that can be converted", FileNotConvertedWarning)
            continue
    return pdfs

def convert(file: str) -> str:
    files = [file]
    pdfs = to_pdf(files)
    return pdfs[0]


def main():
    iface = gr.Interface(
        fn=convert,
        inputs=gr.File(label="Upload your file"),
        outputs=gr.File(label="Converted PDF"),
        title="File to PDF Converter",
        description="Upload a file in .docx, .xlsx, .html, .pptx, .csv, .xml, .md, .jpg/.jpeg, .png format, and get it converted to PDF."
    )
    iface.launch()

if __name__ == "__main__":
    main()
