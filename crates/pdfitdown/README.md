# pdfitdown

**PdfItDown** is a Rust-based tool and library that converts text-based files, images, office documents, and markup files to PDF. It is built on top of [`markdown2pdf`](https://crates.io/crates/markdown2pdf), [`office2pdf`](https://crates.io/crates/office2pdf), and [`image`](https://crates.io/crates/image) crates to carry out fast, reliable conversions.

## Applicability

**PdfItDown** supports the following file formats:

| Category | Formats |
|----------|---------|
| Markup | `.md`, `.html`, `.htm` |
| Office | `.docx`, `.xlsx`, `.pptx` |
| Images | `.png`, `.jpg`, `.jpeg`, `.webp`, `.tiff`, `.avif` |
| Text | `.txt`, `.csv`, `.xml`, `.json`, and more |
| Other | `.pdf` (pass-through) |

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
pdfitdown = "4.0"
```

Or enable parallelization with the `rayon` feature:

```toml
[dependencies]
pdfitdown = { version = "4.0", features = ["rayon"] }
```

### Feature Flags

| Feature | Description | Default |
|---------|-------------|---------|
| `cli` | Command-line interface (`clap`) | ✅ |
| `image` | Image-to-PDF conversion | ✅ |
| `office` | Office document conversion (`docx`, `xlsx`, `pptx`) | ✅ |
| `markup` | Markdown/HTML and text-based format conversion | ✅ |
| `rayon` | Parallelized batch conversion | ❌ |

```toml
# Library only — no CLI, only markup and image support
[dependencies]
pdfitdown = { version = "4.0", default-features = false, features = ["markup", "image"] }

# Minimal — markup only
[dependencies]
pdfitdown = { version = "4.0", default-features = false, features = ["markup"] }
```

## Usage

### Basic Conversion

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
let pdf_bytes = converter.convert("business_growth.md")?;
std::fs::write("business_growth.pdf", pdf_bytes)?;
```

### Convert Multiple Files

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
converter.convert_multiple_files(
    vec!["business_growth.md", "logo.png"],
    vec!["business_growth.pdf", "logo.pdf"],
    true, // overwrite
)?;
```

### Bulk Directory Conversion

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
converter.convert_directory("tests/data/testdir", true, true)?; // overwrite, recursive
```

### From Binary Data

```rust
use pdfitdown::{PdfItDownConverter, types::Converter};

let converter = PdfItDownConverter::new();
let png_bytes = /* binary image data */;
let pdf_bytes = converter.convert(png_bytes)?;
```

## CLI Usage

Install the CLI:

```bash
cargo install pdfitdown
```

Usage:

```
pdfitdown [OPTIONS]

Options:
  -i, --inputfile <INPUTFILE>    Path to the input file(s). Can be used multiple times.
  -o, --outputfile <OUTPUTFILE>  Path to the output PDF file(s).
  -d, --directory <DIRECTORY>    Directory to bulk-convert.
      --no-overwrite             Do not overwrite existing PDF files.
      --recursive                Recursively process directories.
  -h, --help                     Print help.
  -V, --version                  Print version.
```

Examples:

```bash
# Single file
pdfitdown -i README.md -o README.pdf

# Multiple files
pdfitdown -i test0.png -i test1.md -o testoutput0.pdf -o testoutput1.pdf

# Directory bulk conversion
pdfitdown -d tests/data/testdir --recursive
```

## API Overview

The crate exposes a unified `Converter` trait and a composite `PdfItDownConverter` that delegates to specialized converters. Each converter is available only when its corresponding feature is enabled:

| Converter | Feature | Description |
|-----------|---------|-------------|
| `ImageConverter` | `image` | Converts image files to PDF via the `image` crate. |
| `OfficeConverter` | `office` | Converts Word, Excel, and PowerPoint via `office2pdf`. |
| `MarkupConverter` | `markup` | Converts Markdown and HTML via `markdown2pdf`. |
| `TextConverter` | `markup` | Converts plain text and text-based formats via `markdown2pdf`. |

All converters implement:

- `supported_formats()` — Returns the list of supported extensions.
- `convert(input)` — Converts an input (`&str` path, `PathBuf`, or `Vec<u8>`) to PDF bytes.
- `convert_to_file(input, output, overwrite)` — Writes PDF directly to a file.
- `convert_multiple_files(inputs, outputs, overwrite)` — Batch conversion.
- `convert_directory(dir, overwrite, recursive)` — Directory bulk conversion.

## License

MIT License — see the [repository](https://github.com/AstraBert/PdfItDown) for details.
