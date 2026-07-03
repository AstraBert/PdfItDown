#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Convert hyperfine JSON results (optionally including a `memory_usage_byte`
array per result) into a Markdown comparison table.

Usage:
    ./hyperfine_to_md.py results.json
    ./hyperfine_to_md.py results.json --precision 3
    cat results.json | ./hyperfine_to_md.py -
"""

import argparse
import json
import sys
from statistics import mean, stdev


def fmt_time(seconds: float, precision: int) -> str:
    return f"{seconds:.{precision}f} s"


def fmt_bytes(n: float) -> str:
    """Human-readable bytes (binary units)."""
    for unit in ("B", "KiB", "MiB", "GiB"):
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TiB"


def get_pdfitdown_command(command: str) -> str:
    if command.startswith("../../target"):
        return "pdfitdown (rust)"
    elif command.startswith(".venv"):
        return "pdfitdown (python)"
    raise ValueError(f"Unrecognized command: {command}")


def memory_stats(mem_list):
    if not mem_list:
        return None
    return {
        "mean": mean(mem_list),
        "min": min(mem_list),
        "max": max(mem_list),
    }


def build_table(data: dict, precision: int) -> str:
    results = data.get("results", [])
    if not results:
        return "_No results found in input JSON._"

    has_memory = any(r.get("memory_usage_byte") for r in results)

    headers = ["Command", "Mean", "Std Dev", "Min", "Max"]
    if has_memory:
        headers += ["Mean Mem", "Max Mem"]

    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")

    for r in results:
        cmd = get_pdfitdown_command(r["command"])
        row = [
            f"`{cmd}`",
            fmt_time(r["mean"], precision),
            fmt_time(r["stddev"], precision),
            fmt_time(r["min"], precision),
            fmt_time(r["max"], precision),
        ]
        if has_memory:
            mstats = memory_stats(r.get("memory_usage_byte", []))
            if mstats:
                row += [fmt_bytes(mstats["mean"]), fmt_bytes(mstats["max"])]
            else:
                row += ["–", "–"]
        lines.append("| " + " | ".join(row) + " |")

    table = "\n".join(lines)

    # Optional: relative speed comparison vs. fastest
    fastest = min(results, key=lambda r: r["mean"])
    summary_lines = ["", "**Relative performance:**", ""]
    for r in results:
        ratio = r["mean"] / fastest["mean"]
        cmd = get_pdfitdown_command(r["command"])
        if r is fastest:
            summary_lines.append(f"- `{cmd}` — fastest")
        else:
            summary_lines.append(f"- `{cmd}` — {ratio:.2f}x slower")

    return table + "\n" + "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to hyperfine JSON export, or '-' for stdin")
    parser.add_argument(
        "--precision", type=int, default=3, help="Decimal places for times (default: 3)"
    )
    parser.add_argument(
        "-o", "--output", help="Write Markdown to file instead of stdout"
    )
    args = parser.parse_args()

    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        with open(args.input, "r") as f:
            data = json.load(f)

    table = build_table(data, args.precision)

    if args.output:
        with open(args.output, "w") as f:
            f.write(table + "\n")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(table)


if __name__ == "__main__":
    main()
