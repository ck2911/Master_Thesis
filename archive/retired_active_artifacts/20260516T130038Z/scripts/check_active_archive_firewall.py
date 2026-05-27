#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIRS = [ROOT / "src", ROOT / "config", ROOT / "scripts"]
ARCHIVE_SUFFIX = "".join(chr(code) for code in (117, 115))
BANNED_ARCHIVE = "archive" + r"[/\\]" + ARCHIVE_SUFFIX + "_" + "legacy"
BANNED_DATA = "legacy" + "_" + ARCHIVE_SUFFIX
BANNED_FLAT_PACKAGE = "src" + "_" + "flat"
BANNED_NOTEBOOK = "master" + "_" + "pipeline"
BANNED_PATTERNS = {
    "retired archive path": re.compile(BANNED_ARCHIVE, re.IGNORECASE),
    "retired data path": re.compile(BANNED_DATA, re.IGNORECASE),
    "retired flat source package": re.compile(BANNED_FLAT_PACKAGE, re.IGNORECASE),
    "retired notebook pipeline": re.compile(BANNED_NOTEBOOK, re.IGNORECASE),
}


def iter_active_files() -> list[Path]:
    files: list[Path] = []
    for directory in ACTIVE_DIRS:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.name != "check_active_archive_firewall.py":
                files.append(path)
    return sorted(files)


def main() -> int:
    findings: list[tuple[str, str, int, str]] = []
    for path in iter_active_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for label, pattern in BANNED_PATTERNS.items():
                if pattern.search(line):
                    findings.append((label, str(path.relative_to(ROOT)), line_no, line.strip()))

    if findings:
        print("Archive firewall FAILED: active code/config/script references retired archive identifiers.")
        for label, rel_path, line_no, line in findings:
            print(f"- {rel_path}:{line_no}: {label}: {line}")
        return 1

    print("Archive firewall OK: no active code/config/script references retired archive identifiers.")
    print("Scanned files:", len(iter_active_files()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
