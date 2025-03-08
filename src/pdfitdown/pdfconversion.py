# Import required libraries
from markitdown import MarkItDown          # Library for conversion to markdown
try:
    from .markdown_pdf import MarkdownPdf, Section  # Library for PDF generation
except ImportError:
    from markdown_pdf import MarkdownPdf, Section
import os

def convert_to_pdf(
    file_path: str,     # Path to input file
    output_path: str,   # Desired path for output PDF
    title: str = "PDF Title"  # Optional title for the PDF, defaults to "PDF Title"
):
    """
    Converts a .pptx/.xlsx/.docx/.csv/.json/.xml/.html/.zip file to PDF format.
    
    Args:
        file_path: Path to the source .xlsx/.pdf/.pptx/.docx/.csv/.json/.xml/.html/.zip file
        output_path: Where to save the resulting PDF
        title: Title to be set in PDF metadata
    
    Returns:
        str: Path to the generated PDF file
    """
    if os.path.splitext(file_path)[1] not in [".docx", ".html", ".xml", ".csv", ".md", ".pptx", ".xlsx"]:
        raise ValueError(f"ERROR! File format for {file_path} not supported, please provide a file that has one of the following formats:\n\n- "+"\n- ".join([".docx", ".html", ".xml", ".csv", ".md", ".pptx", ".xlsx"]))
    # Initialize markdown converter
    md = MarkItDown()
    
    # Convert file to markdown
    result = md.convert(file_path)
    
    # Extract the text content from the conversion result
    finstr = result.text_content
    
    # Create new PDF document with no table of contents (toc_level=0)
    pdf = MarkdownPdf(toc_level=0)
    
    # Add the converted markdown content as a section in the PDF
    pdf.add_section(Section(finstr))
    
    # Set the PDF document's title in its metadata
    pdf.meta["title"] = title
    
    # Save the PDF to the specified output path
    pdf.save(output_path)
    
    # Return the path where the PDF was saved
    return output_path


def convert_markdown_to_pdf(
    file_path: str,     # Path to input markdown file
    output_path: str,   # Desired path for output PDF
    title: str = "PDF Title"  # Optional title for the PDF, defaults to "PDF Title"
):
    """
    Converts a .md file to PDF format.
    
    Args:
        file_path: Path to the source .md file
        output_path: Where to save the resulting PDF
        title: Title to be set in PDF metadata
    
    Returns:
        str: Path to the generated PDF file
    """
    # Extract the text content from the markdown file
    f = open(file_path, "r")

    finstr = f.read()
    
    # Create new PDF document with no table of contents (toc_level=0)
    pdf = MarkdownPdf(toc_level=0)
    
    # Add the converted markdown content as a section in the PDF
    pdf.add_section(Section(finstr))
    
    # Set the PDF document's title in its metadata
    pdf.meta["title"] = title
    
    # Save the PDF to the specified output path
    pdf.save(output_path)
    
    # Return the path where the PDF was saved
    return output_path