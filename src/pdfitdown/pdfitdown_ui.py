try:
    from .pdfconversion import convert_to_pdf, convert_markdown_to_pdf
except ImportError:
    from pdfconversion import convert_to_pdf, convert_markdown_to_pdf
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
        if f.endswith(".docx"):
            newfile = f.replace(".docx", ".pdf")
            file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
            pdfs.append(file_to_add)
        elif f.endswith(".pdf"):
            pdfs.append(f)
        elif f.endswith(".html"):
            newfile = f.replace(".html", ".pdf")
            file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
            pdfs.append(file_to_add)
        elif f.endswith(".pptx"):
            newfile = f.replace(".pptx", ".pdf")
            file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
            pdfs.append(file_to_add)
        elif f.endswith(".csv"):
            newfile = f.replace(".csv", ".pdf")
            file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
            pdfs.append(file_to_add)
        elif f.endswith(".xlsx"):
            newfile = f.replace(".xlsx", ".pdf")
            file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
            pdfs.append(file_to_add)
        elif f.endswith(".xml"):
            newfile = f.replace(".xml", ".pdf")
            file_to_add = convert_to_pdf(f, newfile, newfile.split(".")[0])
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
        description="Upload a file in .docx, .xlsx, .html, .pptx, .csv, .xml, or .md format, and get it converted to PDF."
    )
    iface.launch()

if __name__ == "__main__":
    main()
