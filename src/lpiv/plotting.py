from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from .specifications import RESULTS_ROOT


def _scale(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    if np.isclose(src_min, src_max):
        return (dst_min + dst_max) / 2.0
    return dst_min + (value - src_min) * (dst_max - dst_min) / (src_max - src_min)


def _points(x_values: pd.Series, y_values: pd.Series, x_min: float, x_max: float, y_min: float, y_max: float) -> str:
    points: list[str] = []
    for x, y in zip(x_values, y_values):
        px = _scale(float(x), x_min, x_max, 70.0, 740.0)
        py = _scale(float(y), y_min, y_max, 430.0, 35.0)
        points.append(f"{px:.2f},{py:.2f}")
    return " ".join(points)


def write_irf_svg(
    table: pd.DataFrame,
    response: str,
    path: Path,
    title: str | None = None,
    band: int = 90,
) -> None:
    subset = table.loc[table["response"].eq(response)].sort_values("horizon").copy()
    if subset.empty:
        return
    lower = f"lower_{band}"
    upper = f"upper_{band}"
    y_columns = ["coefficient"]
    if lower in subset.columns and upper in subset.columns:
        y_columns.extend([lower, upper])
    y_min = float(subset[y_columns].min().min())
    y_max = float(subset[y_columns].max().max())
    padding = (y_max - y_min) * 0.12 if not np.isclose(y_min, y_max) else 1.0
    y_min -= padding
    y_max += padding
    x_min = float(subset["horizon"].min())
    x_max = float(subset["horizon"].max())
    if np.isclose(x_min, x_max):
        x_min -= 1
        x_max += 1

    coefficient_points = _points(subset["horizon"], subset["coefficient"], x_min, x_max, y_min, y_max)
    zero_y = _scale(0.0, y_min, y_max, 430.0, 35.0)
    band_polygon = ""
    if lower in subset.columns and upper in subset.columns:
        upper_points = _points(subset["horizon"], subset[upper], x_min, x_max, y_min, y_max)
        lower_points = _points(subset["horizon"].iloc[::-1], subset[lower].iloc[::-1], x_min, x_max, y_min, y_max)
        band_polygon = f'<polygon points="{upper_points} {lower_points}" fill="#94a3b8" opacity="0.28" />'

    tick_labels = []
    for horizon in subset["horizon"]:
        x = _scale(float(horizon), x_min, x_max, 70.0, 740.0)
        tick_labels.append(
            f'<line x1="{x:.2f}" y1="430" x2="{x:.2f}" y2="436" stroke="#334155" />'
            f'<text x="{x:.2f}" y="455" text-anchor="middle" font-size="12" fill="#334155">{int(horizon)}</text>'
        )

    display_title = escape(title or f"LP-IV IRF: {response}")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <rect width="800" height="500" fill="#ffffff" />
  <text x="70" y="24" font-size="16" font-family="Arial, sans-serif" fill="#0f172a">{display_title}</text>
  <line x1="70" y1="430" x2="740" y2="430" stroke="#334155" />
  <line x1="70" y1="35" x2="70" y2="430" stroke="#334155" />
  <line x1="70" y1="{zero_y:.2f}" x2="740" y2="{zero_y:.2f}" stroke="#64748b" stroke-dasharray="4 4" />
  {band_polygon}
  <polyline points="{coefficient_points}" fill="none" stroke="#0f766e" stroke-width="3" />
  {"".join(tick_labels)}
  <text x="405" y="485" text-anchor="middle" font-size="12" font-family="Arial, sans-serif" fill="#334155">Horizon</text>
  <text x="16" y="240" text-anchor="middle" transform="rotate(-90 16 240)" font-size="12" font-family="Arial, sans-serif" fill="#334155">Response</text>
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def write_irf_svgs(table: pd.DataFrame, output_dir: Path | None = None) -> None:
    target = output_dir or RESULTS_ROOT / "plots"
    target.mkdir(parents=True, exist_ok=True)
    if table.empty or "response" not in table.columns:
        return
    for response in sorted(table["response"].dropna().unique()):
        safe_name = response.replace("/", "_")
        write_irf_svg(table, response=response, path=target / f"irf_{safe_name}.svg")


def write_series_svg(series: pd.Series, path: Path, title: str, y_label: str = "Value") -> None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return
    x_values = pd.Series(range(clean.shape[0]), index=clean.index)
    y_min = float(clean.min())
    y_max = float(clean.max())
    padding = (y_max - y_min) * 0.12 if not np.isclose(y_min, y_max) else 1.0
    y_min -= padding
    y_max += padding
    points = _points(x_values, clean, 0.0, max(float(clean.shape[0] - 1), 1.0), y_min, y_max)
    zero_y = _scale(0.0, y_min, y_max, 430.0, 35.0)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <rect width="800" height="500" fill="#ffffff" />
  <text x="70" y="24" font-size="16" font-family="Arial, sans-serif" fill="#0f172a">{escape(title)}</text>
  <line x1="70" y1="430" x2="740" y2="430" stroke="#334155" />
  <line x1="70" y1="35" x2="70" y2="430" stroke="#334155" />
  <line x1="70" y1="{zero_y:.2f}" x2="740" y2="{zero_y:.2f}" stroke="#64748b" stroke-dasharray="4 4" />
  <polyline points="{points}" fill="none" stroke="#1d4ed8" stroke-width="2.5" />
  <text x="16" y="240" text-anchor="middle" transform="rotate(-90 16 240)" font-size="12" font-family="Arial, sans-serif" fill="#334155">{escape(y_label)}</text>
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
