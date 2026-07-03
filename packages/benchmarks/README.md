# Benchmarks

This folder contains benchmarks comparing the Rust CLI (`pdfitdown`) against its Python equivalent across different parsing backends and Office document types.

## Structure

```
.
├── data/                     # Sample Office documents
│   ├── office1.docx
│   ├── office2.xlsx
│   └── office3.pptx
├── results/
│   ├── lit/                  # Results for the liteparse backend
│   └── markitdown/           # Results for the markitdown backend
├── scripts/                  # Helper scripts (see below)
├── benchmark_report.html     # Interactive HTML report (generated)
├── pyproject-lit.toml        # Python deps for liteparse backend
├── pyproject-markitdown.toml # Python deps for markitdown backend
├── pyproject-native.toml     # Python deps for native backend (>= v4)
└── uv.lock
```

## Scripts

### `scripts/run-hyperfine.sh`

Runs [hyperfine](https://github.com/sharkdp/hyperfine) benchmarks comparing the Rust binary against the Python CLI for each sample document.

**Usage:**

```bash
# Benchmark the liteparse backend
./scripts/run-hyperfine.sh liteparse

# Benchmark the markitdown backend (default)
./scripts/run-hyperfine.sh
```

**What it does:**
- Swaps the appropriate `pyproject-*.toml` into `pyproject.toml`.
- Re-creates the virtual environment with `uv sync`.
- Runs hyperfine with 3 warmups and 20 runs per command, exporting JSON to `results/<backend>/`.
- Restores the original `pyproject.toml` name.

Each benchmark compares:
- `../../target/release/pdfitdown` — the Rust CLI
- `.venv/bin/pdfitdown` — the Python CLI

### `scripts/show-disk-space.sh`

Shows the on-disk size of the `.venv/lib` directory for a given backend configuration.

**Usage:**

```bash
./scripts/show-disk-space.sh liteparse
./scripts/show-disk-space.sh markitdown
./scripts/show-disk-space.sh native
```

This is useful for comparing the dependency bloat of each backend.

### `scripts/json-to-md.sh`

Converts all existing hyperfine JSON results into Markdown tables.

**Usage:**

```bash
./scripts/json-to-md.sh
```

It processes:
- `results/lit/office{1,2,3}.json`
- `results/markitdown/office{1,2,3}.json`

### `scripts/json_to_md.py`

Standalone Python script that converts a single hyperfine JSON export into a Markdown comparison table. It also includes a relative speed summary (e.g., "1.5× slower").

**Usage:**

```bash
uv run scripts/json_to_md.py results/lit/office1.json
uv run scripts/json_to_md.py results/lit/office1.json --precision 2 -o output.md
```

**Features:**
- Reads hyperfine JSON (file or stdin).
- Displays mean, std dev, min, max per command.
- Optionally shows memory usage stats if `memory_usage_byte` is present in the JSON.
- Generates a relative performance summary against the fastest command.

### `scripts/generate_report.py`

Generates a fully self-contained, interactive HTML report (`benchmark_report.html`) that combines benchmark tables with embedded PDF viewers for visual comparison.

**Usage:**

```bash
uv run scripts/generate_report.py
```

**What it includes:**
- Tabbed navigation per document (Office1 / Office2 / Office3)
- Performance tables for both **Liteparse** and **Markitdown** backends
- Relative speed highlighting (fastest in green, slower in red with multiplier)
- Memory usage stats when available
- Side-by-side embedded PDF viewers for each output:
  - `pdfitdown (rust)`
  - `pdfitdown (python) × markitdown`
  - `pdfitdown (python) × liteparse`

The resulting `benchmark_report.html` is a single standalone file (PDFs are inlined as base64) that can be opened directly in any browser.

## Backends

| Backend      | Config file                | Python package constraint |
|--------------|----------------------------|---------------------------|
| liteparse    | `pyproject-lit.toml`       | `pdfitdown<=3.1`          |
| markitdown   | `pyproject-markitdown.toml`| `pdfitdown[markitdown]<=3.1` |
| native       | `pyproject-native.toml`    | `pdfitdown>=4`            |

## Requirements

- [uv](https://docs.astral.sh/uv/) for Python environment management
- [hyperfine](https://github.com/sharkdp/hyperfine) for benchmarking
- The Rust `pdfitdown` binary built at `../../target/release/pdfitdown`
