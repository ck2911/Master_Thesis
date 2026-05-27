#!/usr/bin/env python3
"""Inspect thesis CSV tables and emit LaTeX snippets.

The manuscript references the research tables in place instead of copying or
hand-editing them.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_ROOT = REPO_ROOT / "results" / "final"
TABLE_DIRS = (
    RESULTS_ROOT / "tables",
    RESULTS_ROOT / "diagnostics",
    RESULTS_ROOT / "mechanism",
    RESULTS_ROOT / "robustness",
    RESULTS_ROOT / "regime",
    RESULTS_ROOT / "stability",
    RESULTS_ROOT / "uncertainty",
    RESULTS_ROOT / "proxy_validation",
)
CANONICAL_NAME = re.compile(r"^[a-z0-9][a-z0-9_./-]*\.csv$")


def relative_to_repo(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def label_for(path: Path) -> str:
    rel = path.relative_to(RESULTS_ROOT).with_suffix("").as_posix()
    slug = re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-")
    return f"tab:{slug}"


def title_for(path: Path) -> str:
    return path.stem.replace("_", " ").title()


def iter_tables() -> list[Path]:
    tables: list[Path] = []
    for directory in TABLE_DIRS:
        if directory.exists():
            tables.extend(path for path in directory.rglob("*.csv") if path.is_file())
    return sorted(set(tables))


def row_count(path: Path) -> int:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            next(reader, None)
            return sum(1 for _ in reader)
    except UnicodeDecodeError:
        with path.open(newline="", encoding="latin-1") as handle:
            reader = csv.reader(handle)
            next(reader, None)
            return sum(1 for _ in reader)


def validate(tables: list[Path]) -> list[str]:
    problems: list[str] = []
    if not tables:
        problems.append(f"No thesis CSV tables found under {RESULTS_ROOT}")
    for table in tables:
        rel = relative_to_repo(table)
        if " " in rel:
            problems.append(f"Table path contains spaces: {rel}")
        if not CANONICAL_NAME.match(table.relative_to(RESULTS_ROOT).as_posix()):
            problems.append(f"Table path is not deterministic lowercase snake/kebab case: {rel}")
        if table.stat().st_size == 0:
            problems.append(f"Table is empty: {rel}")
    return problems


def emit_latex(tables: list[Path]) -> str:
    blocks: list[str] = []
    for table in tables:
        rel = relative_to_repo(table)
        blocks.append(
            "\\artifacttable\n"
            f"  {{{title_for(table)}}}\n"
            f"  {{{label_for(table)}}}\n"
            f"  {{../{rel}}}\n"
            f"  {{Canonical CSV table with {row_count(table)} data row(s).}}"
        )
    return "\n\n".join(blocks)


def emit_markdown(tables: list[Path]) -> str:
    lines = ["# Canonical Table Artifacts", ""]
    for table in tables:
        lines.append(f"- `{relative_to_repo(table)}` ({row_count(table)} rows)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if table paths are missing")
    parser.add_argument("--format", choices=("markdown", "latex", "json"), default="markdown")
    args = parser.parse_args()

    tables = iter_tables()
    problems = validate(tables)
    if args.check and problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    if args.format == "latex":
        print(emit_latex(tables))
    elif args.format == "json":
        print(json.dumps([relative_to_repo(path) for path in tables], indent=2))
    else:
        print(emit_markdown(tables))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
