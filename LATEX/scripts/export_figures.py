#!/usr/bin/env python3
"""Inspect thesis figures and emit LaTeX include snippets.

The manuscript references exported figures in place.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURE_ROOT = REPO_ROOT / "results" / "final" / "figures"
VALID_SUFFIXES = {".png", ".pdf", ".jpg", ".jpeg"}
CANONICAL_NAME = re.compile(r"^[a-z0-9][a-z0-9_./-]*\.(png|pdf|jpg|jpeg)$")


def relative_artifact(path: Path) -> str:
    return path.relative_to(FIGURE_ROOT).as_posix()


def label_for(path: str) -> str:
    stem = Path(path).with_suffix("").as_posix()
    slug = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return f"fig:{slug}"


def title_for(path: str) -> str:
    stem = Path(path).stem
    words = re.sub(r"^(monthly_irf_|cumulative_interval_|uncertainty_fan_)", "", stem)
    return words.replace("_", " ").title()


def iter_figures() -> list[Path]:
    if not FIGURE_ROOT.exists():
        return []
    return sorted(
        path
        for path in FIGURE_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in VALID_SUFFIXES
    )


def validate(figures: list[Path]) -> list[str]:
    problems: list[str] = []
    if not figures:
        problems.append(f"No thesis figures found under {FIGURE_ROOT}")
    for figure in figures:
        rel = relative_artifact(figure)
        if " " in rel:
            problems.append(f"Figure path contains spaces: {rel}")
        if not CANONICAL_NAME.match(rel):
            problems.append(f"Figure path is not deterministic lowercase snake/kebab case: {rel}")
    return problems


def emit_latex(figures: list[Path]) -> str:
    blocks: list[str] = []
    for figure in figures:
        rel = relative_artifact(figure)
        blocks.append(
            "\\thesisfigure\n"
            f"  {{{rel}}}\n"
            f"  {{{title_for(rel)}}}\n"
            f"  {{{label_for(rel)}}}"
        )
    return "\n\n".join(blocks)


def emit_markdown(figures: list[Path]) -> str:
    lines = ["# Canonical Figure Artifacts", ""]
    for figure in figures:
        rel = relative_artifact(figure)
        lines.append(f"- `results/final/figures/{rel}`")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if figure paths are missing")
    parser.add_argument("--format", choices=("markdown", "latex", "json"), default="markdown")
    args = parser.parse_args()

    figures = iter_figures()
    problems = validate(figures)
    if args.check and problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    if args.format == "latex":
        print(emit_latex(figures))
    elif args.format == "json":
        print(json.dumps([relative_artifact(path) for path in figures], indent=2))
    else:
        print(emit_markdown(figures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
