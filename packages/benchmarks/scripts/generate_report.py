#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["jinja2"]
# ///
"""
Generate an interactive HTML benchmark report from hyperfine JSON results.

Usage:
    uv run scripts/generate_report.py
"""

import base64
import json
from pathlib import Path

from jinja2 import Template

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"


def fmt_time(seconds: float, precision: int = 3) -> str:
    return f"{seconds:.{precision}f} s"


def fmt_bytes(n: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TiB"


def get_label(command: str) -> str:
    if command.startswith("../../target"):
        return "pdfitdown (rust)"
    elif command.startswith(".venv"):
        return "pdfitdown (python)"
    return command


def parse_result_json(path: Path) -> dict:
    with open(path, "r") as f:
        data = json.load(f)

    results = data.get("results", [])
    parsed = []
    for r in results:
        mem = r.get("memory_usage_byte", [])
        parsed.append(
            {
                "label": get_label(r["command"]),
                "mean": r["mean"],
                "stddev": r["stddev"],
                "min": r["min"],
                "max": r["max"],
                "mean_mem": fmt_bytes(sum(mem) / len(mem)) if mem else None,
                "max_mem": fmt_bytes(max(mem)) if mem else None,
            }
        )

    fastest = min(parsed, key=lambda x: x["mean"])
    for p in parsed:
        p["ratio"] = p["mean"] / fastest["mean"]
        p["is_fastest"] = p is fastest

    return {"results": parsed}


def b64_pdf(path: Path) -> str | None:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_office_data(office_num: int) -> dict:
    office_id = f"office{office_num}"

    lit_json = RESULTS_DIR / "lit" / f"{office_id}.json"
    markitdown_json = RESULTS_DIR / "markitdown" / f"{office_id}.json"

    lit = parse_result_json(lit_json) if lit_json.exists() else None
    markitdown = parse_result_json(markitdown_json) if markitdown_json.exists() else None

    return {
        "id": office_id,
        "lit": lit,
        "markitdown": markitdown,
        "pdfs": {
            "rust": b64_pdf(DATA_DIR / f"{office_id}-rs.pdf"),
            "py_markitdown": b64_pdf(DATA_DIR / f"{office_id}-py.pdf"),
            "py_liteparse": b64_pdf(DATA_DIR / f"{office_id}-lit-py.pdf"),
        },
    }


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PdfItDown Benchmark Report</title>
  <style>
    :root {
      --bg: #0d1117;
      --surface: #161b22;
      --surface-hover: #1f242c;
      --border: #30363d;
      --text: #c9d1d9;
      --text-secondary: #8b949e;
      --accent: #58a6ff;
      --accent-dim: #1f6feb;
      --success: #3fb950;
      --danger: #f85149;
      --warning: #d29922;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }
    header {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1.5rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    header h1 { margin: 0; font-size: 1.5rem; }
    header p { margin: 0.25rem 0 0; color: var(--text-secondary); font-size: 0.9rem; }
    .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }

    /* Tabs */
    .tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .tab-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      padding: 0.6rem 1.2rem;
      border-radius: 8px;
      cursor: pointer;
      font-size: 0.95rem;
      transition: all 0.15s;
    }
    .tab-btn:hover { background: var(--surface-hover); color: var(--text); }
    .tab-btn.active { background: var(--accent-dim); color: #fff; border-color: var(--accent); }

    /* Sections */
    .section { display: none; }
    .section.active { display: block; animation: fadeIn 0.2s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }
    .card h2 { margin: 0 0 1rem; font-size: 1.2rem; color: var(--accent); }
    .card h3 { margin: 1.5rem 0 0.75rem; font-size: 1rem; color: var(--text); }

    /* Tables */
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
    th { color: var(--text-secondary); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; }
    tr:hover td { background: var(--surface-hover); }
    .fastest { color: var(--success); font-weight: 600; }
    .slower { color: var(--danger); }

    /* PDF grid */
    .pdf-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .pdf-card {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .pdf-card-header {
      padding: 0.75rem 1rem;
      background: var(--surface-hover);
      border-bottom: 1px solid var(--border);
      font-size: 0.85rem;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .pdf-card-header .tag {
      font-size: 0.7rem;
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      background: var(--accent-dim);
      color: #fff;
    }
    .pdf-card-header .tag.rust { background: var(--success); }
    .pdf-card-header .tag.python { background: var(--warning); color: #000; }
    .pdf-card iframe {
      flex: 1;
      width: 100%;
      height: 500px;
      border: none;
      background: #fff;
    }
    .pdf-card .missing {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-secondary);
      font-size: 0.9rem;
      height: 500px;
    }

    .no-data { color: var(--text-secondary); font-style: italic; }
  </style>
</head>
<body>
  <header>
    <h1>📊 PdfItDown Benchmark Report</h1>
    <p>Rust vs. Python — performance &amp; output comparison across document types and backends</p>
  </header>

  <div class="container">
    <div class="tabs" id="mainTabs">
      {% for office in offices %}
      <button class="tab-btn {% if loop.first %}active{% endif %}" data-target="{{ office.id }}">
        {{ office.id | upper }}
      </button>
      {% endfor %}
    </div>

    {% for office in offices %}
    <div id="{{ office.id }}" class="section {% if loop.first %}active{% endif %}">

      <!-- Liteparse Backend -->
      <div class="card">
        <h2>🚀 Liteparse Backend</h2>
        {% if office.lit %}
        <table>
          <thead>
            <tr>
              <th>Command</th>
              <th>Mean</th>
              <th>Std Dev</th>
              <th>Min</th>
              <th>Max</th>
              {% if office.lit.results[0].mean_mem %}
              <th>Mean Mem</th>
              <th>Max Mem</th>
              {% endif %}
              <th>Relative</th>
            </tr>
          </thead>
          <tbody>
            {% for r in office.lit.results %}
            <tr>
              <td><code>{{ r.label }}</code></td>
              <td>{{ "%.3f" | format(r.mean) }} s</td>
              <td>{{ "%.3f" | format(r.stddev) }} s</td>
              <td>{{ "%.3f" | format(r.min) }} s</td>
              <td>{{ "%.3f" | format(r.max) }} s</td>
              {% if r.mean_mem %}
              <td>{{ r.mean_mem }}</td>
              <td>{{ r.max_mem }}</td>
              {% endif %}
              <td>
                {% if r.is_fastest %}
                <span class="fastest">fastest</span>
                {% else %}
                <span class="slower">{{ "%.2f" | format(r.ratio) }}× slower</span>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% else %}
        <p class="no-data">No liteparse benchmark data available.</p>
        {% endif %}
      </div>

      <!-- Markitdown Backend -->
      <div class="card">
        <h2>📝 Markitdown Backend</h2>
        {% if office.markitdown %}
        <table>
          <thead>
            <tr>
              <th>Command</th>
              <th>Mean</th>
              <th>Std Dev</th>
              <th>Min</th>
              <th>Max</th>
              {% if office.markitdown.results[0].mean_mem %}
              <th>Mean Mem</th>
              <th>Max Mem</th>
              {% endif %}
              <th>Relative</th>
            </tr>
          </thead>
          <tbody>
            {% for r in office.markitdown.results %}
            <tr>
              <td><code>{{ r.label }}</code></td>
              <td>{{ "%.3f" | format(r.mean) }} s</td>
              <td>{{ "%.3f" | format(r.stddev) }} s</td>
              <td>{{ "%.3f" | format(r.min) }} s</td>
              <td>{{ "%.3f" | format(r.max) }} s</td>
              {% if r.mean_mem %}
              <td>{{ r.mean_mem }}</td>
              <td>{{ r.max_mem }}</td>
              {% endif %}
              <td>
                {% if r.is_fastest %}
                <span class="fastest">fastest</span>
                {% else %}
                <span class="slower">{{ "%.2f" | format(r.ratio) }}× slower</span>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
        {% else %}
        <p class="no-data">No markitdown benchmark data available.</p>
        {% endif %}
      </div>

      <!-- PDF Comparison -->
      <div class="card">
        <h2>📄 Output PDF Comparison</h2>
        <div class="pdf-grid">
          {% set pdfs = [
            ("Rust CLI", office.pdfs.rust, "rust"),
            ("Python — Markitdown", office.pdfs.py_markitdown, "python"),
            ("Python — Liteparse", office.pdfs.py_liteparse, "python")
          ] %}
          {% for name, b64, tag in pdfs %}
          <div class="pdf-card">
            <div class="pdf-card-header">
              <span>{{ name }}</span>
              <span class="tag {{ tag }}">{{ tag | upper }}</span>
            </div>
            {% if b64 %}
            <iframe src="data:application/pdf;base64,{{ b64 }}"></iframe>
            {% else %}
            <div class="missing">PDF not found</div>
            {% endif %}
          </div>
          {% endfor %}
        </div>
      </div>

    </div>
    {% endfor %}
  </div>

  <script>
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.target).classList.add('active');
      });
    });
  </script>
</body>
</html>
"""


def main():
    offices = [build_office_data(i) for i in range(1, 4)]

    template = Template(HTML_TEMPLATE)
    html = template.render(offices=offices)

    out_path = ROOT / "benchmark_report.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
