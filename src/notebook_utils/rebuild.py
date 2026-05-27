"""Refresh thesis results from inside the notebook when needed."""

from __future__ import annotations

import subprocess
import sys

from .artifacts import warn_missing
from .display import Markdown, display
from .paths import PIPELINE_SCRIPT, ROOT


def _tail(text: str, max_chars: int = 12000) -> str:
    if not text:
        return ""
    return text if len(text) <= max_chars else text[-max_chars:]


def run_full_rebuild_if_requested(rebuild_results: bool) -> None:
    if not rebuild_results:
        return

    if not PIPELINE_SCRIPT.exists():
        warn_missing(PIPELINE_SCRIPT)
        raise SystemExit("Full rebuild requested, but scripts/run_full_pipeline.py is missing.")

    display(Markdown("_Refreshing the stored empirical outputs before rendering the notebook._"))
    completed = subprocess.run(
        [sys.executable, str(PIPELINE_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        if completed.stdout:
            print("\n--- captured stdout (tail) ---")
            print(_tail(completed.stdout))
        if completed.stderr:
            print("\n--- captured stderr (tail) ---")
            print(_tail(completed.stderr))
        raise SystemExit(f"Full rebuild failed with exit code {completed.returncode}; see captured output above.")
    display(Markdown("_Empirical outputs refreshed; rendering thesis presentation._"))
