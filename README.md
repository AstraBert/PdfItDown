<div align="center">
<h1>PdfItDown</h1>
<h2>Convert Everything to PDF</h2>
</div>
<br>
<div align="center">
    <img src="https://raw.githubusercontent.com/AstraBert/PdfItDown/main/img/logo.png" alt="PdfItDown Logo">
</div>

> [!IMPORTANT]
> `markdown-pdf` is now implemented, with support for `PyMuPdf` v1.25.1, internally in `PdfItDown`. Make sure to install the latest version of the package (from 0.0.4 on) to avoid errors such as the one in [this issue](https://github.com/AstraBert/PdfItDown/issues/1) 

**PdfItDown** is a python package that relies on [`markitdown` by Microsoft](https://github.com/microsoft/markitdown/) and (a slightly modified version of) [`markdown_pdf`](https://github.com/vb64/markdown-pdf). 

### Applicability

**PdfItDown** is applicable to the following file formats:

- Markdown
- PowerPoint
- Word
- Excel
- HTML
- Text-based formats (CSV, XML)
- ZIP files (iterates over contents)

### How does it work?

**PdfItDown** works in a very simple way:

- From **markdown** to PDF

```mermaid
graph LR
2(Input File) --> 3[Markdown content] 
3[Markdown content] --> 4[markdown-pdf]
4[markdown-pdf] --> 5(PDF file)
```

- From other **text-based** file formats to PDF

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

You can now use the **command line tool**:

```
usage: pdfitdown [-h] -i INPUTFILE -o OUTPUTFILE [-t TITLE]

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputfile INPUTFILE
                        Path to the input file that needs to be converted to PDF
  -o OUTPUTFILE, --outputfile OUTPUTFILE
                        Path to the output PDF file
  -t TITLE, --title TITLE
                        Title to include in the PDF metadata. Default: 'PDF Title'
```

An example usage can be:

```bash
pdfitdown -i README.md -o README.pdf -t "README"
```

Or you can use it **inside your python scripts**:

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

Or you can just launch a [Gradio](https://gradio.app)-based user interface:

```bash
pdfitdown_ui
```

You will be able to see the application running on `http://localhost:7860` within seconds!

Watch the demo here:

[![Watch the video demo!](https://raw.githubusercontent.com/AstraBert/PdfItDown/main/img/thumbnail.png)](https://raw.githubusercontent.com/AstraBert/PdfItDown/main/img/pdfitdown_ui_demo.mp4)

### Contributing

Contributions are always welcome!

Find contribution guidelines at [CONTRIBUTING.md](https://github.com/AstraBert/PdfItDown/tree/main/CONTRIBUTING.md)

### License and Funding

This project is open-source and is provided under an [MIT License](https://github.com/AstraBert/PdfItDown/tree/main/LICENSE).

If you found it useful, please consider [funding it](https://github.com/sponsors/AstraBert).