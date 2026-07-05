# pdfitdown-worker

A Cloudflare Worker that converts files to PDF using a Rust/WASM backend.

## Overview

This Worker exposes a single HTTP endpoint that accepts a file via POST request and returns a generated PDF binary. It supports all file formats that [PdfItDown](https://github.com/AstraBert/PdfItDown) handles:

- **Markdown** (`.md`)
- **HTML** (`.html`, `.htm`)
- **PowerPoint** (`.pptx`)
- **Word** (`.docx`)
- **Excel** (`.xlsx`)
- **Text-based formats** (`.txt`, `.csv`, `.xml`, `.json`, and more)
- **Image files** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.tiff`, `.avif`)
- **PDF** (pass-through)

## How It Works

- Receives a file as raw bytes in the POST body
- Uses [`@cle-does-things/pdfitdown-wasm`](https://www.npmjs.com/package/@cle-does-things/pdfitdown-wasm) (Rust-compiled to WASM) to auto-detect the format and convert to PDF
- Returns the PDF as `application/octet-stream`

## Development

```bash
# Install dependencies
pnpm install

# Copy the WASM module into the project root
pnpm run cp-wasm

# Run locally
pnpm run dev

# Run tests
pnpm test

# Deploy to Cloudflare
pnpm run deploy
```

## API

### `POST /`

Converts a file to PDF.

**Request Body:** Raw file bytes (`application/octet-stream`)

**Response:** PDF binary (`application/octet-stream`)

**Examples:**

```bash
# Convert Markdown
curl -X POST http://localhost:8787/ \
  -H "Content-Type: application/octet-stream" \
  --data-binary "# Hello World\n\nThis is **bold** text." \
  --output output.pdf

# Convert an image
curl -X POST http://localhost:8787/ \
  -H "Content-Type: application/octet-stream" \
  --data-binary @photo.png \
  --output photo.pdf

# Convert a Word document
curl -X POST http://localhost:8787/ \
  -H "Content-Type: application/octet-stream" \
  --data-binary @document.docx \
  --output document.pdf
```

## Project Structure

```
.
├── src/
│   └── index.ts          # Worker entry point
├── test/
│   └── index.spec.ts     # Vitest tests
├── pdfitdown_wasm_bg.wasm # WASM module (copied from npm package)
├── wrangler.jsonc        # Cloudflare Workers config
└── vitest.config.mts     # Test configuration
```

## Tech Stack

- [Cloudflare Workers](https://workers.cloudflare.com/)
- [Wrangler](https://developers.cloudflare.com/workers/wrangler/)
- [Vitest](https://vitest.dev/) with `@cloudflare/vitest-pool-workers`
- Rust/WASM via `@cle-does-things/pdfitdown-wasm`
