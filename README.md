<div align="center">
<h1>PdfItDown</h1>
<h2>Convert Everything to PDF</h2>
</div>
<br>
<div align="center">
    <a href="https://discord.gg/AXcVf269"><img src="https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white" alt="Join Discord Server" width=200 height=60></a>
</div>
<br>
<div align="center">
    <img src="https://raw.githubusercontent.com/AstraBert/PdfItDown/main/img/logo.png" alt="PdfItDown Logo">
</div>

[Looking for the legacy python package?](https://github.com/AstraBert/PdfItDown/tree/v3)

**PdfItDown** is a Rust-based tool and library that converts text-based files, images, office documents, and markup files to PDF. It is built on top of [`markdown2pdf`](https://crates.io/crates/markdown2pdf), [`office2pdf`](https://crates.io/crates/office2pdf), and [`image`](https://crates.io/crates/image) crates to carry out fast, reliable conversions. Visit us on our [documentation website](https://pdfitdown.eu)!

### Applicability

**PdfItDown** is applicable to the following file formats:

- Markdown (`.md`)
- HTML (`.html`, `.htm`)
- PowerPoint (`.pptx`)
- Word (`.docx`)
- Excel (`.xlsx`)
- Text-based formats (`.txt`, `.csv`, `.xml`, `.json`, and more)
- Image files (`.png`, `.jpg`, `.jpeg`, `.webp`, `.tiff`, `.avif`)
- PDF (pass-through)

### How does it work?

**PdfItDown** works in a very simple way:

- From **markdown / HTML** to PDF

```mermaid
graph LR
2(Input File) --> 3[Markdown content]
3[Markdown content] --> 4[markdown2pdf]
4[markdown2pdf] --> 5(PDF file)
```

- From **image** to PDF

```mermaid
graph LR
2(Input File) --> 3[Bytes]
3[Bytes] --> 4[image crate]
4[image crate] --> 5(PDF file)
```

- From **Office documents** to PDF

```mermaid
graph LR
2(Input File) --> 3[office2pdf]
3[office2pdf] --> 4(PDF file)
```

- From other **text-based** file formats to PDF

```mermaid
graph LR
2(Input File) --> 3[Text content]
3[Text content] --> 4[markdown2pdf]
4[markdown2pdf] --> 5(PDF file)
```

### Installation and Usage

**PdfItDown** is distributed as a Rust crate and a standalone CLI binary.

#### Install the CLI

```bash
# Install from crates.io
cargo install pdfitdown

# Or build from source
git clone https://github.com/AstraBert/PdfItDown.git
cd PdfItDown
cargo install --path crates/pdfitdown
```

> **Note:** The CLI requires the `cli` feature (enabled by default). To install the library only without CLI support, use `cargo install pdfitdown --no-default-features`.

You can now use the **command line tool**:

```
Usage: pdfitdown [OPTIONS]

  PdfItDown CLI: convert any file format to PDF

Options:
  -i, --inputfile <INPUTFILE>    Path to the input file(s) that need to be converted to PDF. Can be used multiple times.
  -o, --outputfile <OUTPUTFILE>  Path to the output PDF file(s). If more than one input file is provided, you should provide an equal number of output files.
  -d, --directory <DIRECTORY>    Directory whose files you want to bulk-convert to PDF. If `--inputfile` is also provided, this option will be ignored.
      --no-overwrite             Do not overwrite existing PDF files
      --recursive                Recursively go through a directory when converting files to PDFs
  -h, --help                     Print help
  -V, --version                  Print version
```

An example usage can be:

```bash
pdfitdown -i README.md -o README.pdf
```

Or you can use it **inside your Rust projects**:

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
let pdf_bytes = converter.convert("business_growth.md")?;
std::fs::write("business_growth.pdf", pdf_bytes)?;
```

You can also convert **multiple files at once**:

- In the CLI:

```bash
# with custom output paths
pdfitdown -i test0.png -i test1.md -o testoutput0.pdf -o testoutput1.pdf
```

- In the Rust API:

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
converter.convert_multiple_files(
    vec!["business_growth.md", "logo.png"],
    vec!["business_growth.pdf", "logo.pdf"],
    true, // overwrite
)?;
```

You can bulk-convert **all the files in a directory**:

- In the CLI:

```bash
# non-recursive
pdfitdown -d tests/data/testdir
# recursive
pdfitdown -d tests/data/testdir --recursive
```

- In the Rust API:

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
converter.convert_directory("tests/data/testdir", true, true)?; // overwrite, recursive
```

#### Feature Flags

PdfItDown uses Cargo features to let you choose which converters to include:

| Feature | Description | Default |
|---------|-------------|---------|
| `cli` | Enables the command-line interface and `clap` dependency | ✅ |
| `image` | Enables image-to-PDF conversion (`png`, `jpg`, etc.) | ✅ |
| `office` | Enables Office document conversion (`docx`, `xlsx`, `pptx`) | ✅ |
| `markup` | Enables Markdown/HTML conversion and text-based formats | ✅ |
| `rayon` | Enables parallelized batch conversion | ❌ |

**Examples:**

```toml
# Library only, no CLI
[dependencies]
pdfitdown = { version = "4.0", default-features = false, features = ["markup", "image"] }

# All converters + parallelization
[dependencies]
pdfitdown = { version = "4.0", features = ["rayon"] }
```

```bash
# Install CLI with all features
cargo install pdfitdown --features rayon

# Install library only (e.g. for WASM or embedded use)
cargo install pdfitdown --no-default-features --features markup
```

### Python Legacy

Looking for the legacy Python package? It is available on the [`v3` branch](https://github.com/AstraBert/PdfItDown/tree/v3) and on PyPI as `pdfitdown<4.0`.


### License

This project is open-source and is provided under an [MIT License](https://github.com/AstraBert/PdfItDown/tree/main/LICENSE).
