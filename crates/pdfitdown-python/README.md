# pdfitdown

Python bindings for **PdfItDown** — a Rust library that converts text-based files, images, office documents, and markup files to PDF.

## Installation

```bash
uv add pdfitdown
```

Or build from source with Maturin:

```bash
git clone https://github.com/AstraBert/PdfItDown.git
cd PdfItDown/crates/pdfitdown-python
maturin build --release
uv pip install target/wheels/pdfitdown-*.whl
```

## Supported Formats

| Category | Formats |
|----------|---------|
| Markup | `.md`, `.html`, `.htm` |
| Office | `.docx`, `.xlsx`, `.pptx` |
| Images | `.png`, `.jpg`, `.jpeg`, `.webp`, `.tiff`, `.avif` |
| Text | `.txt`, `.csv`, `.xml`, `.json`, and more |
| Other | `.pdf` (pass-through) |

## Usage

### Command Line Interface

The Python package installs a CLI entry point:

```bash
# Convert a single file
pdfitdown -i README.md -o README.pdf

# Convert multiple files
pdfitdown -i file1.png -i file2.docx -o out1.pdf -o out2.pdf

# Bulk convert a directory
pdfitdown -d ./documents --recursive
```

### Python API

The python API is as similar as possible to [v3](https://github.com/AstraBert/PdfItDown/tree/v3)

```python
from pdfitdown.pdfconversion import Converter

# Convert a single file
converter = Converter()
result = converter.convert("README.md", "README.pdf", overwrite=False)
results = converter.multiple_convert(["business.md", "report.docx"])
directory_results = converter.convert_directory("docs/", overwrite=True, recursive=True)
```

The package exposes a thin Python wrapper around the Rust [`PdfItDownConverter`](./src/lib.rs), which handles format detection and delegates to specialized image, office, markup, and text converters.

## License

MIT License — see the [repository](https://github.com/AstraBert/PdfItDown) for details.
