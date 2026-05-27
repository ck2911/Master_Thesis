#!/usr/bin/env python3
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "results" / "lpiv" / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.lpiv.diagnostics import identification_contribution
from src.lpiv.horizon_design import complete_horizon_frame
from src.lpiv.inference import fit_ols, hac_bandwidth_for_horizon, normal_critical_value
from src.lpiv.local_projection_iv import estimate_specification, results_to_frame
from src.lpiv.regime_interactions import estimate_regime_interactions, regime_results_to_frame
from src.lpiv.specifications import (
    BASELINE_RESPONSES,
    DEFAULT_HORIZONS,
    REGIME_NAMES,
    RESULTS_ROOT,
    baseline_specification,
    prepare_lpiv_dataset,
    validate_specification_data,
)


CANONICAL_DIR = RESULTS_ROOT / "canonical_baseline"
CUMULATIVE_DIR = RESULTS_ROOT / "cumulative_irfs"
PERSISTENCE_DIR = RESULTS_ROOT / "persistence"
WEAK_IV_DIR = RESULTS_ROOT / "weak_iv_validation"
REGIME_DIR = RESULTS_ROOT / "regime_irfs"
DAX_DIR = RESULTS_ROOT / "dax_robustness"

RESPONSE_LABELS = {
    "ln_ecb_assets_ea_stock": "ECB assets",
    "ln_hh_loans_ea_stock": "Household loans",
    "ln_nfc_loans_ea_stock": "NFC loans",
    "ln_house_price_de_real": "Real house prices",
    "ln_compensation_ea20_real": "Real compensation",
}


def ensure_output_dirs() -> None:
    for directory in [
        CANONICAL_DIR,
        CUMULATIVE_DIR,
        PERSISTENCE_DIR,
        WEAK_IV_DIR,
        REGIME_DIR,
        DAX_DIR,
        RESULTS_ROOT / ".matplotlib",
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def weak_iv_flag(f_stat: float) -> str:
    if pd.isna(f_stat):
        return "missing"
    if f_stat > 10:
        return "strong"
    if f_stat >= 5:
        return "moderate_caution"
    return "weak_iv_risk"


def canonicalize_table(table: pd.DataFrame) -> pd.DataFrame:
    output = table.copy()
    output["beta"] = output["coefficient"]
    output["HAC_se"] = output["std_error"]
    output["F_stat"] = output["first_stage_f_stat"]
    output["partial_R2"] = output["first_stage_partial_r_squared"]
    output["CI_68_low"] = output["lower_68"]
    output["CI_68_high"] = output["upper_68"]
    output["CI_low"] = output["lower_90"]
    output["CI_high"] = output["upper_90"]
    output["CI_95_low"] = output["lower_95"]
    output["CI_95_high"] = output["upper_95"]
    output["weak_iv_flag"] = output["F_stat"].map(weak_iv_flag)
    ordered = [
        "response",
        "horizon",
        "beta",
        "HAC_se",
        "t_stat",
        "p_value",
        "CI_low",
        "CI_high",
        "CI_68_low",
        "CI_68_high",
        "CI_95_low",
        "CI_95_high",
        "F_stat",
        "partial_R2",
        "weak_iv_flag",
        "nobs",
        "sample_start",
        "sample_end",
        "hac_bandwidth",
        "controls",
    ]
    return output[ordered].sort_values(["response", "horizon"]).reset_index(drop=True)


def write_baseline_tables(summary: pd.DataFrame) -> None:
    summary.to_csv(CANONICAL_DIR / "baseline_summary_table.csv", index=False)
    first_stage = summary[
        [
            "response",
            "horizon",
            "F_stat",
            "partial_R2",
            "weak_iv_flag",
            "nobs",
            "sample_start",
            "sample_end",
        ]
    ].copy()
    first_stage.to_csv(CANONICAL_DIR / "horizon_first_stage_diagnostics.csv", index=False)
    for response in BASELINE_RESPONSES:
        subset = summary.loc[summary["response"].eq(response)].copy()
        subset.to_csv(CANONICAL_DIR / f"irf_{response}.csv", index=False)


def _configure_axis(ax: plt.Axes) -> None:
    ax.axhline(0.0, color="#111827", linewidth=0.9, linestyle="-", alpha=0.8)
    ax.grid(True, axis="y", color="#e5e7eb", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_irf_with_fstat(table: pd.DataFrame, response: str, output_dir: Path) -> None:
    subset = table.loc[table["response"].eq(response)].sort_values("horizon").copy()
    if subset.empty:
        return

    x = subset["horizon"].to_numpy(dtype=float)
    beta = subset["beta"].to_numpy(dtype=float)
    ci68_low = subset["CI_68_low"].to_numpy(dtype=float)
    ci68_high = subset["CI_68_high"].to_numpy(dtype=float)
    ci90_low = subset["CI_low"].to_numpy(dtype=float)
    ci90_high = subset["CI_high"].to_numpy(dtype=float)
    f_stat = subset["F_stat"].to_numpy(dtype=float)

    fig, (ax, ax_f) = plt.subplots(
        2,
        1,
        figsize=(7.3, 5.4),
        sharex=True,
        gridspec_kw={"height_ratios": [3.2, 1.0], "hspace": 0.08},
    )

    ax.fill_between(x, ci90_low, ci90_high, color="#93c5fd", alpha=0.28, label="90% CI")
    ax.fill_between(x, ci68_low, ci68_high, color="#2563eb", alpha=0.24, label="68% CI")
    ax.plot(x, beta, color="#0f172a", linewidth=2.0, marker="o", markersize=4.5, label="LP-IV beta")
    weak = subset["weak_iv_flag"].eq("weak_iv_risk").to_numpy()
    moderate = subset["weak_iv_flag"].eq("moderate_caution").to_numpy()
    if weak.any():
        ax.scatter(x[weak], beta[weak], marker="x", s=54, color="#b91c1c", linewidths=1.8, label="F < 5")
    if moderate.any():
        ax.scatter(x[moderate], beta[moderate], marker="D", s=34, color="#b45309", label="5 <= F < 10")
    _configure_axis(ax)
    ax.set_ylabel("Response")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    ax.set_title(f"Canonical baseline LP-IV: {RESPONSE_LABELS.get(response, response)}", loc="left")
    ax.legend(loc="best", frameon=False, fontsize=8, ncol=2)

    ax_f.plot(x, f_stat, color="#475569", linewidth=1.8, marker="o", markersize=3.8)
    ax_f.axhline(10.0, color="#15803d", linestyle="--", linewidth=0.9)
    ax_f.axhline(5.0, color="#b91c1c", linestyle="--", linewidth=0.9)
    ax_f.fill_between(x, 0, 5, color="#fee2e2", alpha=0.55)
    ax_f.set_ylabel("F-stat")
    ax_f.set_xlabel("Horizon")
    ax_f.set_xticks(list(DEFAULT_HORIZONS))
    ax_f.grid(True, axis="y", color="#e5e7eb", linewidth=0.8)
    ax_f.spines["top"].set_visible(False)
    ax_f.spines["right"].set_visible(False)
    ax_f.set_ylim(bottom=0)

    fig.text(
        0.01,
        0.01,
        "Weak-IV protocol: F < 5 weak-IV risk; 5 <= F < 10 moderate caution.",
        fontsize=7.5,
        color="#475569",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"irf_{response}.png", dpi=220)
    fig.savefig(output_dir / f"irf_{response}.svg")
    plt.close(fig)


def cumulative_irfs(summary: pd.DataFrame) -> pd.DataFrame:
    z68 = normal_critical_value(0.68)
    z90 = normal_critical_value(0.90)
    rows: list[dict[str, object]] = []
    for response, subset in summary.groupby("response"):
        running_beta = 0.0
        running_var = 0.0
        min_f = math.inf
        for _, row in subset.sort_values("horizon").iterrows():
            running_beta += float(row["beta"])
            running_var += float(row["HAC_se"]) ** 2
            min_f = min(min_f, float(row["F_stat"]))
            running_se = math.sqrt(running_var)
            rows.append(
                {
                    "response": response,
                    "horizon": int(row["horizon"]),
                    "cumulative_response": running_beta,
                    "cumulative_HAC_se_independence_approx": running_se,
                    "CI_68_low": running_beta - z68 * running_se,
                    "CI_68_high": running_beta + z68 * running_se,
                    "CI_low": running_beta - z90 * running_se,
                    "CI_high": running_beta + z90 * running_se,
                    "min_F_stat_to_horizon": min_f,
                    "weak_iv_flag_to_horizon": weak_iv_flag(min_f),
                    "ci_method": "sum_of_reported_horizon_betas_with_independence_se_approximation",
                }
            )
    return pd.DataFrame(rows)


def plot_cumulative_irf(table: pd.DataFrame, response: str, output_dir: Path) -> None:
    subset = table.loc[table["response"].eq(response)].sort_values("horizon").copy()
    if subset.empty:
        return
    x = subset["horizon"].to_numpy(dtype=float)
    y = subset["cumulative_response"].to_numpy(dtype=float)
    ci68_low = subset["CI_68_low"].to_numpy(dtype=float)
    ci68_high = subset["CI_68_high"].to_numpy(dtype=float)
    ci90_low = subset["CI_low"].to_numpy(dtype=float)
    ci90_high = subset["CI_high"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(7.1, 4.2))
    ax.fill_between(x, ci90_low, ci90_high, color="#c7d2fe", alpha=0.34, label="90% CI")
    ax.fill_between(x, ci68_low, ci68_high, color="#4f46e5", alpha=0.22, label="68% CI")
    ax.plot(x, y, color="#111827", linewidth=2.1, marker="o", markersize=4.5)
    _configure_axis(ax)
    ax.set_xticks(list(DEFAULT_HORIZONS))
    ax.set_xlabel("Horizon")
    ax.set_ylabel("Cumulative response")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    ax.set_title(f"Cumulative baseline response: {RESPONSE_LABELS.get(response, response)}", loc="left")
    ax.legend(loc="best", frameon=False, fontsize=8)
    fig.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"cumulative_irf_{response}.png", dpi=220)
    fig.savefig(output_dir / f"cumulative_irf_{response}.svg")
    plt.close(fig)


def plot_baseline_comparison(
    table: pd.DataFrame,
    responses: tuple[str, str],
    output_dir: Path,
    filename: str,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7.1, 4.2))
    for response in responses:
        subset = table.loc[table["response"].eq(response)].sort_values("horizon")
        if subset.empty:
            continue
        ax.plot(
            subset["horizon"],
            subset["beta"],
            marker="o",
            linewidth=2.0,
            label=RESPONSE_LABELS.get(response, response),
        )
    _configure_axis(ax)
    ax.set_xticks(list(DEFAULT_HORIZONS))
    ax.set_xlabel("Horizon")
    ax.set_ylabel("Response")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    ax.set_title(title, loc="left")
    ax.legend(loc="best", frameon=False, fontsize=8)
    fig.text(0.01, 0.01, "All plotted baseline horizons are weak-IV-risk horizons.", fontsize=7.5, color="#475569")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{filename}.png", dpi=220)
    fig.savefig(output_dir / f"{filename}.svg")
    plt.close(fig)


def persistence_metrics(summary: pd.DataFrame, cumulative: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for response, subset in summary.groupby("response"):
        ordered = subset.sort_values("horizon").reset_index(drop=True)
        beta = ordered["beta"].to_numpy(dtype=float)
        horizons = ordered["horizon"].to_numpy(dtype=int)
        if np.all(np.isnan(beta)):
            continue
        peak_idx = int(np.nanargmax(np.abs(beta)))
        peak_beta = float(beta[peak_idx])
        peak_horizon = int(horizons[peak_idx])
        peak_sign = np.sign(peak_beta)
        same_sign_horizons = horizons[np.sign(beta) == peak_sign] if peak_sign != 0 else np.array([], dtype=int)
        persistence_duration = (
            int(same_sign_horizons.max() - same_sign_horizons.min()) if same_sign_horizons.size else np.nan
        )
        half_life = np.nan
        return_to_zero = np.nan
        if peak_sign != 0:
            after_peak = ordered.loc[ordered["horizon"].ge(peak_horizon)].copy()
            half_threshold = abs(peak_beta) / 2.0
            half_candidates = after_peak.loc[after_peak["beta"].abs().le(half_threshold), "horizon"]
            if not half_candidates.empty:
                half_life = int(half_candidates.iloc[0] - peak_horizon)
            zero_candidates = after_peak.loc[
                (np.sign(after_peak["beta"]) != peak_sign)
                | ((after_peak["CI_low"] <= 0.0) & (after_peak["CI_high"] >= 0.0)),
                "horizon",
            ]
            if not zero_candidates.empty:
                return_to_zero = int(zero_candidates.iloc[0])
        cumulative_final = float(
            cumulative.loc[
                cumulative["response"].eq(response) & cumulative["horizon"].eq(cumulative["horizon"].max()),
                "cumulative_response",
            ].iloc[0]
        )
        rows.append(
            {
                "variable": response,
                "peak_beta": peak_beta,
                "peak_horizon": peak_horizon,
                "persistence_duration_quarters_reported_grid": persistence_duration,
                "same_sign_reported_horizons": ",".join(str(h) for h in same_sign_horizons),
                "half_life_quarters_after_peak": half_life,
                "return_to_zero_horizon": return_to_zero,
                "cumulative_response_h12": cumulative_final,
                "min_F_stat": float(ordered["F_stat"].min()),
                "weak_iv_flag": weak_iv_flag(float(ordered["F_stat"].min())),
            }
        )
    return pd.DataFrame(rows)


def estimate_ols_comparison(data: pd.DataFrame, spec, canonical_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    iv_lookup = canonical_summary.set_index(["response", "horizon"])
    for response in spec.responses:
        for horizon in spec.horizons:
            frame, outcome, control_columns = complete_horizon_frame(
                data,
                response=response,
                horizon=horizon,
                controls=spec.resolved_control_variables(),
                control_lags=spec.control_lags,
                required_current=[spec.endogenous_policy, spec.instrument],
            )
            x_columns = [spec.endogenous_policy, *control_columns]
            ols = fit_ols(
                frame[outcome],
                frame[x_columns],
                hac_bandwidth=hac_bandwidth_for_horizon(horizon),
                method="ols_lp_hac",
            )
            iv_row = iv_lookup.loc[(response, horizon)]
            ols_beta = float(ols.coefficients[spec.endogenous_policy])
            iv_beta = float(iv_row["beta"])
            rows.append(
                {
                    "response": response,
                    "horizon": horizon,
                    "ols_beta": ols_beta,
                    "ols_HAC_se": float(ols.std_errors[spec.endogenous_policy]),
                    "ols_t_stat": float(ols.t_statistics[spec.endogenous_policy]),
                    "ols_p_value": float(ols.p_values[spec.endogenous_policy]),
                    "lpiv_beta": iv_beta,
                    "lpiv_HAC_se": float(iv_row["HAC_se"]),
                    "lpiv_p_value": float(iv_row["p_value"]),
                    "F_stat": float(iv_row["F_stat"]),
                    "weak_iv_flag": iv_row["weak_iv_flag"],
                    "sign_agreement": bool(np.sign(ols_beta) == np.sign(iv_beta)),
                    "abs_lpiv_to_ols_ratio": np.nan if math.isclose(ols_beta, 0.0) else abs(iv_beta / ols_beta),
                    "nobs": int(ols.nobs),
                }
            )
    return pd.DataFrame(rows)


def lag_robustness(data: pd.DataFrame, spec) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for lags in (1, 2, 4):
        lag_spec = spec.with_updates(name=f"lag_{lags}", control_lags=lags)
        validate_specification_data(data, lag_spec)
        lag_table = canonicalize_table(results_to_frame(estimate_specification(lag_spec, data=data)))
        lag_table.insert(0, "control_lags", lags)
        rows.append(lag_table)
    return pd.concat(rows, ignore_index=True)


def instrument_concentration(data: pd.DataFrame, spec) -> None:
    regime, quarter = identification_contribution(data, spec)
    regime.to_csv(WEAK_IV_DIR / "instrument_regime_concentration.csv", index=False)
    quarter.head(15).to_csv(WEAK_IV_DIR / "top_instrument_quarters.csv", index=False)

    frame = data.copy()
    periods = pd.PeriodIndex(frame["quarter"], freq="Q")
    windows = {
        "gfc_2008_2009": ("2008Q1", "2009Q4"),
        "euro_crisis_2011_2012": ("2011Q1", "2012Q4"),
        "covid_2020_2021": ("2020Q1", "2021Q4"),
        "tightening_2022_baseline": ("2022Q1", "2022Q2"),
    }
    frame["abs_instrument"] = frame[spec.instrument].abs()
    frame["sq_instrument"] = frame[spec.instrument] ** 2
    total_abs = frame["abs_instrument"].sum()
    total_sq = frame["sq_instrument"].sum()
    rows = []
    for name, (start, end) in windows.items():
        mask = (periods >= pd.Period(start, freq="Q")) & (periods <= pd.Period(end, freq="Q"))
        subset = frame.loc[mask]
        rows.append(
            {
                "window": name,
                "start": start,
                "end": end,
                "quarters": int(subset.shape[0]),
                "event_count": int(pd.to_numeric(subset.get("event_count", 0), errors="coerce").fillna(0).sum()),
                "abs_instrument_sum": float(subset["abs_instrument"].sum()),
                "abs_instrument_share": float(subset["abs_instrument"].sum() / total_abs) if total_abs else np.nan,
                "sq_instrument_sum": float(subset["sq_instrument"].sum()),
                "sq_instrument_share": float(subset["sq_instrument"].sum() / total_sq) if total_sq else np.nan,
            }
        )
    pd.DataFrame(rows).to_csv(WEAK_IV_DIR / "instrument_crisis_concentration.csv", index=False)


def plot_fstat_paths(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for response, subset in summary.groupby("response"):
        ordered = subset.sort_values("horizon")
        ax.plot(
            ordered["horizon"],
            ordered["F_stat"],
            marker="o",
            linewidth=1.6,
            label=RESPONSE_LABELS.get(response, response),
        )
    ax.axhline(10.0, color="#15803d", linestyle="--", linewidth=0.9, label="F = 10")
    ax.axhline(5.0, color="#b91c1c", linestyle="--", linewidth=0.9, label="F = 5")
    ax.fill_between(list(DEFAULT_HORIZONS), 0, 5, color="#fee2e2", alpha=0.55)
    ax.set_xticks(list(DEFAULT_HORIZONS))
    ax.set_xlabel("Horizon")
    ax.set_ylabel("First-stage F-statistic")
    ax.set_title("Canonical baseline horizon-specific relevance", loc="left")
    ax.grid(True, axis="y", color="#e5e7eb")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="best", frameon=False, fontsize=7.5, ncol=2)
    fig.tight_layout()
    fig.savefig(WEAK_IV_DIR / "fstat_paths.png", dpi=220)
    fig.savefig(WEAK_IV_DIR / "fstat_paths.svg")
    plt.close(fig)


def regime_outputs(data: pd.DataFrame, spec) -> None:
    regime_spec = spec.with_updates(name="canonical_baseline_regime")
    regime_table = regime_results_to_frame(estimate_regime_interactions(regime_spec, data=data))
    if regime_table.empty:
        return
    regime_table["beta"] = regime_table["coefficient"]
    regime_table["HAC_se"] = regime_table["std_error"]
    regime_table["CI_68_low"] = regime_table["lower_68"]
    regime_table["CI_68_high"] = regime_table["upper_68"]
    regime_table["CI_low"] = regime_table["lower_90"]
    regime_table["CI_high"] = regime_table["upper_90"]
    regime_table["F_stat"] = regime_table["set_first_stage_f_stat"]
    regime_table["partial_R2"] = regime_table["set_first_stage_partial_r_squared"]
    regime_table["weak_iv_flag"] = regime_table["F_stat"].map(weak_iv_flag)
    keep = [
        "response",
        "regime",
        "horizon",
        "beta",
        "HAC_se",
        "t_stat",
        "p_value",
        "CI_low",
        "CI_high",
        "CI_68_low",
        "CI_68_high",
        "F_stat",
        "partial_R2",
        "weak_iv_flag",
        "nobs",
    ]
    regime_out = regime_table[keep].sort_values(["response", "regime", "horizon"])
    regime_out.to_csv(REGIME_DIR / "regime_irf_summary_table.csv", index=False)

    cumulative_rows = []
    comparison_rows = []
    for (response, regime), subset in regime_out.groupby(["response", "regime"]):
        ordered = subset.sort_values("horizon")
        running = 0.0
        for _, row in ordered.iterrows():
            running += float(row["beta"])
            cumulative_rows.append(
                {
                    "response": response,
                    "regime": regime,
                    "horizon": int(row["horizon"]),
                    "cumulative_response": running,
                    "F_stat": float(row["F_stat"]),
                    "weak_iv_flag": row["weak_iv_flag"],
                }
            )
        peak_idx = int(np.nanargmax(np.abs(ordered["beta"].to_numpy(dtype=float))))
        peak_row = ordered.iloc[peak_idx]
        peak_sign = np.sign(float(peak_row["beta"]))
        same_sign = ordered.loc[np.sign(ordered["beta"]) == peak_sign, "horizon"]
        comparison_rows.append(
            {
                "response": response,
                "regime": regime,
                "peak": float(peak_row["beta"]),
                "peak_horizon": int(peak_row["horizon"]),
                "persistence": ",".join(str(int(h)) for h in same_sign),
                "cumulative": running,
                "min_F_stat": float(ordered["F_stat"].min()),
                "weak_iv_flag": weak_iv_flag(float(ordered["F_stat"].min())),
            }
        )
    cumulative_regime = pd.DataFrame(cumulative_rows)
    cumulative_regime.to_csv(REGIME_DIR / "regime_cumulative_irfs.csv", index=False)
    pd.DataFrame(comparison_rows).to_csv(REGIME_DIR / "regime_comparison_table.csv", index=False)

    for response, subset in regime_out.groupby("response"):
        fig, ax = plt.subplots(figsize=(7.1, 4.2))
        for regime in REGIME_NAMES:
            line = subset.loc[subset["regime"].eq(regime)].sort_values("horizon")
            if line.empty:
                continue
            ax.plot(line["horizon"], line["beta"], marker="o", linewidth=1.8, label=regime)
        _configure_axis(ax)
        ax.set_xticks(list(DEFAULT_HORIZONS))
        ax.set_xlabel("Horizon")
        ax.set_ylabel("Response")
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
        ax.set_title(f"Regime LP-IV responses: {RESPONSE_LABELS.get(response, response)}", loc="left")
        ax.legend(loc="best", frameon=False, fontsize=8)
        fig.tight_layout()
        fig.savefig(REGIME_DIR / f"regime_irf_{response}.png", dpi=220)
        fig.savefig(REGIME_DIR / f"regime_irf_{response}.svg")
        plt.close(fig)

    for response in ("ln_house_price_de_real", "ln_hh_loans_ea_stock", "ln_compensation_ea20_real"):
        subset = cumulative_regime.loc[cumulative_regime["response"].eq(response)]
        if subset.empty:
            continue
        fig, ax = plt.subplots(figsize=(7.1, 4.2))
        for regime in REGIME_NAMES:
            line = subset.loc[subset["regime"].eq(regime)].sort_values("horizon")
            if line.empty:
                continue
            ax.plot(line["horizon"], line["cumulative_response"], marker="o", linewidth=1.8, label=regime)
        _configure_axis(ax)
        ax.set_xticks(list(DEFAULT_HORIZONS))
        ax.set_xlabel("Horizon")
        ax.set_ylabel("Cumulative response")
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
        ax.set_title(f"Regime cumulative response: {RESPONSE_LABELS.get(response, response)}", loc="left")
        ax.legend(loc="best", frameon=False, fontsize=8)
        fig.tight_layout()
        fig.savefig(REGIME_DIR / f"regime_cumulative_{response}.png", dpi=220)
        fig.savefig(REGIME_DIR / f"regime_cumulative_{response}.svg")
        plt.close(fig)


def dax_robustness(data: pd.DataFrame, baseline_summary: pd.DataFrame) -> None:
    dax_spec = baseline_specification(
        name="dax_augmented",
        output_subdir="dax_robustness",
        include_dax_control=True,
    )
    dax_table = canonicalize_table(results_to_frame(estimate_specification(dax_spec, data=data)))
    dax_table.to_csv(DAX_DIR / "dax_augmented_summary_table.csv", index=False)
    baseline = baseline_summary[["response", "horizon", "beta", "HAC_se", "F_stat", "partial_R2"]].rename(
        columns={
            "beta": "baseline_beta",
            "HAC_se": "baseline_HAC_se",
            "F_stat": "baseline_F_stat",
            "partial_R2": "baseline_partial_R2",
        }
    )
    dax = dax_table[["response", "horizon", "beta", "HAC_se", "F_stat", "partial_R2"]].rename(
        columns={
            "beta": "dax_augmented_beta",
            "HAC_se": "dax_augmented_HAC_se",
            "F_stat": "dax_augmented_F_stat",
            "partial_R2": "dax_augmented_partial_R2",
        }
    )
    comparison = baseline.merge(dax, on=["response", "horizon"], how="inner")
    comparison["beta_change"] = comparison["dax_augmented_beta"] - comparison["baseline_beta"]
    comparison["abs_beta_change"] = comparison["beta_change"].abs()
    comparison["baseline_weak_iv_flag"] = comparison["baseline_F_stat"].map(weak_iv_flag)
    comparison["dax_augmented_weak_iv_flag"] = comparison["dax_augmented_F_stat"].map(weak_iv_flag)
    comparison.to_csv(DAX_DIR / "baseline_vs_dax_augmented_comparison.csv", index=False)

    for response in BASELINE_RESPONSES:
        subset = comparison.loc[comparison["response"].eq(response)].sort_values("horizon")
        if subset.empty:
            continue
        fig, ax = plt.subplots(figsize=(7.1, 4.2))
        ax.plot(subset["horizon"], subset["baseline_beta"], marker="o", linewidth=1.9, label="baseline")
        ax.plot(subset["horizon"], subset["dax_augmented_beta"], marker="s", linewidth=1.9, label="DAX-augmented")
        _configure_axis(ax)
        ax.set_xticks(list(DEFAULT_HORIZONS))
        ax.set_xlabel("Horizon")
        ax.set_ylabel("Response")
        ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
        ax.set_title(f"DAX robustness: {RESPONSE_LABELS.get(response, response)}", loc="left")
        ax.legend(loc="best", frameon=False, fontsize=8)
        fig.tight_layout()
        fig.savefig(DAX_DIR / f"dax_comparison_{response}.png", dpi=220)
        fig.savefig(DAX_DIR / f"dax_comparison_{response}.svg")
        plt.close(fig)


def write_run_manifest(summary: pd.DataFrame) -> None:
    lines = [
        "# Canonical Baseline LP-IV Run Manifest",
        "",
        f"- Response-horizon cells: {summary.shape[0]}",
        f"- Responses: {', '.join(BASELINE_RESPONSES)}",
        f"- Horizons: {', '.join(str(h) for h in DEFAULT_HORIZONS)}",
        f"- Minimum F-statistic: {summary['F_stat'].min():.4f}",
        f"- Maximum F-statistic: {summary['F_stat'].max():.4f}",
        "",
        "Weak-IV flags are embedded in all baseline tables and figures.",
    ]
    (CANONICAL_DIR / "run_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_output_dirs()
    spec = baseline_specification(name="canonical_baseline", output_subdir="canonical_baseline")
    data = prepare_lpiv_dataset(spec)
    validate_specification_data(data, spec)

    raw_results = estimate_specification(spec, data=data)
    canonical_summary = canonicalize_table(results_to_frame(raw_results))
    write_baseline_tables(canonical_summary)
    for response in BASELINE_RESPONSES:
        plot_irf_with_fstat(canonical_summary, response, CANONICAL_DIR)
    plot_baseline_comparison(
        canonical_summary,
        ("ln_hh_loans_ea_stock", "ln_nfc_loans_ea_stock"),
        CANONICAL_DIR,
        "credit_channel_hh_vs_nfc",
        "Credit channel comparison: household vs NFC loans",
    )
    plot_baseline_comparison(
        canonical_summary,
        ("ln_house_price_de_real", "ln_compensation_ea20_real"),
        CANONICAL_DIR,
        "financial_vs_real_housing_vs_compensation",
        "Financial vs real comparison: housing vs compensation",
    )
    write_run_manifest(canonical_summary)

    cumulative = cumulative_irfs(canonical_summary)
    cumulative.to_csv(CUMULATIVE_DIR / "cumulative_irf_summary_table.csv", index=False)
    for response in BASELINE_RESPONSES:
        cumulative.loc[cumulative["response"].eq(response)].to_csv(
            CUMULATIVE_DIR / f"cumulative_irf_{response}.csv",
            index=False,
        )
        plot_cumulative_irf(cumulative, response, CUMULATIVE_DIR)

    persistence = persistence_metrics(canonical_summary, cumulative)
    persistence.to_csv(PERSISTENCE_DIR / "persistence_metrics.csv", index=False)

    relevance = canonical_summary[
        ["response", "horizon", "F_stat", "partial_R2", "weak_iv_flag", "nobs", "sample_start", "sample_end"]
    ].copy()
    relevance.to_csv(WEAK_IV_DIR / "horizon_specific_relevance.csv", index=False)
    estimate_ols_comparison(data, spec, canonical_summary).to_csv(WEAK_IV_DIR / "ols_vs_lpiv_comparison.csv", index=False)
    lag_robustness(data, spec).to_csv(WEAK_IV_DIR / "lag_robustness_1_2_4.csv", index=False)
    instrument_concentration(data, spec)
    plot_fstat_paths(canonical_summary)

    regime_outputs(data, spec)
    dax_robustness(data, canonical_summary)

    print("Canonical baseline LP-IV execution complete.")
    print(f"Baseline cells: {canonical_summary.shape[0]}")
    print(f"Minimum first-stage F-statistic: {canonical_summary['F_stat'].min():.4f}")


if __name__ == "__main__":
    main()
