from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def set_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "font.size": 9,
        }
    )


def plot_time_series(data: pd.DataFrame, path: Path, title: str) -> None:
    set_style()
    fig, axes = plt.subplots(len(data.columns), 1, figsize=(9, 1.7 * len(data.columns)), sharex=True)
    if len(data.columns) == 1:
        axes = [axes]
    for ax, col in zip(axes, data.columns):
        ax.plot(data.index, data[col], linewidth=1.2)
        ax.set_title(col, loc="left")
        ax.axvline(pd.Timestamp("2020-03-31"), color="black", linewidth=0.8, linestyle="--", alpha=0.55)
    fig.suptitle(title, y=0.995, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_proxy_irfs(irf_table: pd.DataFrame, path: Path, title: str) -> None:
    set_style()
    variables = list(irf_table["response"].drop_duplicates())
    fig, axes = plt.subplots(len(variables), 1, figsize=(7, 1.7 * len(variables)), sharex=True)
    if len(variables) == 1:
        axes = [axes]
    for ax, variable in zip(axes, variables):
        subset = irf_table.loc[irf_table["response"] == variable]
        ax.plot(subset["horizon"], subset["irf"], linewidth=1.4)
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(variable, loc="left")
    axes[-1].set_xlabel("Months after shock")
    fig.suptitle(title, y=0.995, fontsize=12)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

