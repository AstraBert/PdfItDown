<div align="center">
<h1>PdfItDown</h1>
<h2>Convert Everything to PDF</h2>
</div>
<br>
<div align="center">
    <img src="https://raw.githubusercontent.com/AstraBert/PdfItDown/main/logo.png" alt="PdfItDown Logo">
</div>

**PdfItDown** is a python package that relies on [`markitdown` by Microsoft](https://github.com/microsoft/markitdown/) and [`markdown_pdf`](https://github.com/vb64/markdown-pdf). 

### Applicability

**PdfItDown** is applicable to the following file formats:

- Markdown
- PowerPoint
- Word
- Excel
- HTML
- Text-based formats (CSV, JSON, XML)
- ZIP files (iterates over contents)

### How does it work?

**PdfItDown** works in a very simple way:

```mermaid
graph LR
2(Input File) -->  3[markitdown]
3[markitdown] -->  4[Markdown content]
4[Markdown content] --> 5[markdown-pdf]
5[markdown-pdf] --> 6(PDF file)
```

### Installation and Usage

To install **PdfItDown**, just run:

```bash
python3 -m pip install pdfitdown
```

And then you can simply use it inside your python scripts:

- To convert **.pptx/.docx/.csv/.json/.xml/.html/.zip file to PDF**

```python
from pdfitdown.pdfconversion import convert_to_pdf

output_pdf = convert_to_pdf(file_path = "BusinessGrowth.xlsx", output_path = "business_growth.pdf", title = "Business Growth")
```

- To convert a **.md file to PDF**:

```python
from pdfitdown.pdfconversion import convert_markdown_to_pdf

output_pdf = convert_markdown_to_pdf(file_path = "BusinessGrowth.md", output_path = "business_growth.pdf", title = "Business Growth")
```

In these examples, you will find the output PDF under `business_growth.pdf`.

### Contributing

Contributions are always welcome!

Find contribution guidelines at [CONTRIBUTING.md](https://github.com/AstraBert/PdfItDown/tree/main/CONTRIBUTING.md)

### License and Funding

This project is open-source and is provided under an [MIT License](https://github.com/AstraBert/PdfItDown/tree/main/LICENSE).

If you found it useful, please consider [funding it](https://github.com/sponsors/AstraBert).