# PdfItDown Node Bindings

> Convert (almost) anything to PDF — fast, native Node.js bindings powered by Rust (NAPI-RS).

## Installation

```bash
npm install @cle-does-things/pdfitdown
# or
yarn add @cle-does-things/pdfitdown
```

Prebuilt binaries are available for:

- macOS (x86_64, arm64)
- Linux (x86_64, arm64, musl)
- Windows (x86_64, arm64)

## Supported Formats

- **Office:** DOCX, PPTX, XLSX
- **Markup:** HTML, Markdown
- **Images:** WebP, PNG, JPG, and more
- **Text:** Plain text files

## Usage

### Convert a single file

```typescript
import { PdfItDownConverter } from '@cle-does-things/pdfitdown'

const converter = new PdfItDownConverter()
converter.convertFile('input.docx', 'output.pdf', true)
```

### Convert multiple files

```typescript
const converter = new PdfItDownConverter()
converter.convertMultipleFiles(
  ['file1.docx', 'file2.pptx'],
  ['file1.pdf', 'file2.pdf'],
  true, // overwrite existing
)
```

### Convert a directory

```typescript
const converter = new PdfItDownConverter()
converter.convertDirectory('./documents', true, true) // overwrite, recursive
```

### Convert from memory (Buffer → Buffer)

```typescript
import { readFileSync, writeFileSync } from 'fs'

const converter = new PdfItDownConverter()
const input = readFileSync('input.docx')
const output = converter.convertBytes(input)
writeFileSync('output.pdf', output)
```

## API

```typescript
class PdfItDownConverter {
  constructor()

  /** Convert a file on disk. */
  convertFile(inputFile: string, outputFile: string, overwrite: boolean): void

  /** Convert multiple files in one call. */
  convertMultipleFiles(inputFiles: string[], outputFiles: string[], overwrite: boolean): void

  /** Convert all supported files in a directory. */
  convertDirectory(directory: string, overwrite: boolean, recursive: boolean): void

  /** Convert a Buffer in memory and return a PDF Buffer. */
  convertBytes(input: Buffer): Buffer
}
```

## Development

This is a [NAPI-RS](https://napi.rs) project. To build from source you need Rust and Node.js installed.

```bash
# Development build
yarn build:debug

# Release build
yarn build

# Run tests
yarn test

# Format code
yarn format
```

## License

MIT
