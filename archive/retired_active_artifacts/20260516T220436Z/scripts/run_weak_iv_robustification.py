#!/usr/bin/env python3
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "results" / "lpiv" / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.lpiv.horizon_design import complete_horizon_frame
from src.lpiv.inference import fit_ols, hac_bandwidth_for_horizon, normal_critical_value
from src.lpiv.local_projection_iv import estimate_specification, results_to_frame
from src.lpiv.specifications import (
    BASELINE_RESPONSES,
    DEFAULT_HORIZONS,
    REGIME_NAMES,
    ROBUSTNESS_SAMPLE,
    RESULTS_ROOT,
    baseline_specification,
    prepare_lpiv_dataset,
    validate_specification_data,
)


WEAK_ROOT = RESULTS_ROOT / "weak_iv_robust"
WEAK_BASELINE_DIR = WEAK_ROOT / "baseline"
WEAK_REGIME_DIR = WEAK_ROOT / "regime"
WEAK_TABLE_DIR = WEAK_ROOT / "tables"
WEAK_PLOT_DIR = WEAK_ROOT / "plots"
OLS_ROOT = RESULTS_ROOT / "ols_comparison"
OLS_TABLE_DIR = OLS_ROOT / "tables"
OLS_PLOT_DIR = OLS_ROOT / "plots"
OLS_DIAG_DIR = OLS_ROOT / "diagnostics"
STABILITY_ROOT = RESULTS_ROOT / "stability"
REGIME_DIR = RESULTS_ROOT / "regime_irfs"
DAX_DIR = RESULTS_ROOT / "dax_robustness"
CUMULATIVE_DIR = RESULTS_ROOT / "cumulative_irfs"
CANONICAL_DIR = RESULTS_ROOT / "canonical_baseline"

ALPHA = 0.10

RESPONSE_LABELS = {
    "ln_ecb_assets_ea_stock": "ECB assets",
    "ln_hh_loans_ea_stock": "Household loans",
    "ln_nfc_loans_ea_stock": "NFC loans",
    "ln_house_price_de_real": "Real house prices",
    "ln_compensation_ea20_real": "Real compensation",
}

CHANNEL_NAMES = {
    "ln_ecb_assets_ea_stock": "ECB assets",
    "ln_hh_loans_ea_stock": "HH credit",
    "ln_nfc_loans_ea_stock": "NFC credit",
    "ln_house_price_de_real": "Housing",
    "ln_compensation_ea20_real": "Compensation",
}


@dataclass(frozen=True)
class ARResult:
    p_value: float
    statistic: float
    ci_lower: float
    ci_upper: float
    reject: bool
    bounded: bool
    grid_min: float
    grid_max: float


def ensure_dirs() -> None:
    for directory in [
        WEAK_BASELINE_DIR,
        WEAK_REGIME_DIR,
        WEAK_TABLE_DIR,
        WEAK_PLOT_DIR,
        OLS_TABLE_DIR,
        OLS_PLOT_DIR,
        OLS_DIAG_DIR,
        STABILITY_ROOT,
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


def signed(value: float, tol: float = 0.0) -> int:
    if pd.isna(value):
        return 0
    if value > tol:
        return 1
    if value < -tol:
        return -1
    return 0


def sign_label(value: float) -> str:
    sign = signed(value)
    if sign > 0:
        return "positive"
    if sign < 0:
        return "negative"
    return "zero"


def ar_test_p_value(
    y: pd.Series,
    endogenous: pd.Series,
    instrument: pd.Series,
    controls: pd.DataFrame,
    beta_null: float,
    hac_bandwidth: int,
) -> tuple[float, float]:
    transformed = y - beta_null * endogenous
    x = pd.concat([instrument.rename(instrument.name), controls], axis=1)
    result = fit_ols(transformed, x, hac_bandwidth=hac_bandwidth, method="anderson_rubin_hac")
    coefficient = instrument.name
    t_stat = float(result.t_statistics.get(coefficient, np.nan))
    if pd.isna(t_stat):
        return np.nan, np.nan
    statistic = t_stat**2
    p_value = float(math.erfc(abs(t_stat) / math.sqrt(2.0)))
    return p_value, statistic


def ar_confidence_interval(
    y: pd.Series,
    endogenous: pd.Series,
    instrument: pd.Series,
    controls: pd.DataFrame,
    beta_hat: float,
    beta_se: float,
    ols_beta: float,
    hac_bandwidth: int,
    alpha: float = ALPHA,
    grid_points: int = 801,
) -> ARResult:
    null_p, null_stat = ar_test_p_value(y, endogenous, instrument, controls, 0.0, hac_bandwidth)
    y_std = float(pd.to_numeric(y, errors="coerce").std(ddof=1))
    x_std = float(pd.to_numeric(endogenous, errors="coerce").std(ddof=1))
    scale_candidates = [
        abs(beta_hat),
        abs(beta_se) * 6.0 if not pd.isna(beta_se) else np.nan,
        abs(ols_beta),
        abs(y_std / x_std) if x_std and not math.isclose(x_std, 0.0) else np.nan,
        1e-12,
    ]
    scale = max(float(v) for v in scale_candidates if not pd.isna(v) and np.isfinite(v))
    grid_max = max(scale * 40.0, 1e-10)

    accepted: np.ndarray | None = None
    grid: np.ndarray | None = None
    for _ in range(5):
        grid = np.linspace(-grid_max, grid_max, grid_points)
        p_values = np.array(
            [
                ar_test_p_value(y, endogenous, instrument, controls, float(beta0), hac_bandwidth)[0]
                for beta0 in grid
            ]
        )
        accepted = p_values >= alpha
        if not accepted.any():
            break
        if not accepted[0] and not accepted[-1]:
            break
        grid_max *= 5.0

    if grid is None or accepted is None or not accepted.any():
        return ARResult(
            p_value=null_p,
            statistic=null_stat,
            ci_lower=np.nan,
            ci_upper=np.nan,
            reject=bool(null_p < alpha) if not pd.isna(null_p) else False,
            bounded=False,
            grid_min=-grid_max,
            grid_max=grid_max,
        )

    accepted_grid = grid[accepted]
    lower = float(accepted_grid.min())
    upper = float(accepted_grid.max())
    lower_unbounded = bool(accepted[0])
    upper_unbounded = bool(accepted[-1])
    bounded = not lower_unbounded and not upper_unbounded
    if lower_unbounded:
        lower = -np.inf
    if upper_unbounded:
        upper = np.inf
    return ARResult(
        p_value=null_p,
        statistic=null_stat,
        ci_lower=lower,
        ci_upper=upper,
        reject=bool(null_p < alpha) if not pd.isna(null_p) else False,
        bounded=bounded,
        grid_min=float(grid.min()),
        grid_max=float(grid.max()),
    )


def canonicalize_table(table: pd.DataFrame) -> pd.DataFrame:
    output = table.copy()
    output["beta"] = output["coefficient"]
    output["HAC_se"] = output["std_error"]
    output["F_stat"] = output["first_stage_f_stat"]
    output["partial_R2"] = output["first_stage_partial_r_squared"]
    output["CI_low"] = output["lower_90"]
    output["CI_high"] = output["upper_90"]
    output["weak_iv_flag"] = output["F_stat"].map(weak_iv_flag)
    return output[
        [
            "response",
            "horizon",
            "beta",
            "HAC_se",
            "t_stat",
            "p_value",
            "CI_low",
            "CI_high",
            "F_stat",
            "partial_R2",
            "weak_iv_flag",
            "nobs",
            "sample_start",
            "sample_end",
            "hac_bandwidth",
        ]
    ].sort_values(["response", "horizon"])


def estimate_ols(data: pd.DataFrame, spec) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
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
            rows.append(
                {
                    "response": response,
                    "horizon": horizon,
                    "ols_beta": float(ols.coefficients[spec.endogenous_policy]),
                    "ols_HAC_se": float(ols.std_errors[spec.endogenous_policy]),
                    "ols_t_stat": float(ols.t_statistics[spec.endogenous_policy]),
                    "ols_p_value": float(ols.p_values[spec.endogenous_policy]),
                    "ols_CI_low": float(ols.confidence_intervals([0.90]).loc[spec.endogenous_policy, "lower_90"]),
                    "ols_CI_high": float(ols.confidence_intervals([0.90]).loc[spec.endogenous_policy, "upper_90"]),
                    "nobs": int(ols.nobs),
                    "sample_start": frame["quarter"].min(),
                    "sample_end": frame["quarter"].max(),
                    "hac_bandwidth": hac_bandwidth_for_horizon(horizon),
                }
            )
    return pd.DataFrame(rows)


def cumulative_from_coefficients(table: pd.DataFrame, value_col: str, prefix: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for response, subset in table.groupby("response"):
        running = 0.0
        for _, row in subset.sort_values("horizon").iterrows():
            running += float(row[value_col])
            rows.append(
                {
                    "response": response,
                    "horizon": int(row["horizon"]),
                    f"{prefix}_cumulative": running,
                    f"{prefix}_cumulative_sign": sign_label(running),
                }
            )
    return pd.DataFrame(rows)


def first_turning_point(horizons: pd.Series, values: pd.Series) -> float:
    ordered = pd.DataFrame({"horizon": horizons, "value": values}).sort_values("horizon")
    signs = [signed(v) for v in ordered["value"]]
    nonzero = [(int(h), s) for h, s in zip(ordered["horizon"], signs) if s != 0]
    if not nonzero:
        return np.nan
    initial = nonzero[0][1]
    for horizon, sign in nonzero[1:]:
        if sign != initial:
            return float(horizon)
    return np.nan


def structural_ols_comparison(iv: pd.DataFrame, ols: pd.DataFrame) -> pd.DataFrame:
    merged = iv.merge(ols, on=["response", "horizon"], how="inner")
    iv_cumulative = cumulative_from_coefficients(iv, "beta", "iv")
    ols_cumulative = cumulative_from_coefficients(ols.rename(columns={"ols_beta": "beta"}), "beta", "ols")
    merged = merged.merge(iv_cumulative, on=["response", "horizon"], how="left")
    merged = merged.merge(ols_cumulative, on=["response", "horizon"], how="left")
    turning_rows = []
    for response, subset in merged.groupby("response"):
        iv_turn = first_turning_point(subset["horizon"], subset["beta"])
        ols_turn = first_turning_point(subset["horizon"], subset["ols_beta"])
        if pd.isna(iv_turn) and pd.isna(ols_turn):
            diff = 0.0
        elif pd.isna(iv_turn) or pd.isna(ols_turn):
            diff = np.nan
        else:
            diff = abs(float(iv_turn) - float(ols_turn))
        turning_rows.append(
            {
                "response": response,
                "iv_turning_point": iv_turn,
                "ols_turning_point": ols_turn,
                "turning_point_difference": diff,
            }
        )
    merged = merged.merge(pd.DataFrame(turning_rows), on="response", how="left")
    merged["sign_agreement"] = merged.apply(lambda r: signed(r["beta"]) == signed(r["ols_beta"]), axis=1)
    merged["persistence_agreement"] = merged.apply(
        lambda r: r["iv_cumulative_sign"] == r["ols_cumulative_sign"], axis=1
    )
    merged["cumulative_direction_match"] = merged["persistence_agreement"]
    merged["IV_vs_OLS_ratio"] = merged.apply(
        lambda r: np.nan if math.isclose(float(r["ols_beta"]), 0.0) else float(r["beta"] / r["ols_beta"]),
        axis=1,
    )
    return merged[
        [
            "response",
            "horizon",
            "ols_beta",
            "ols_HAC_se",
            "ols_p_value",
            "beta",
            "HAC_se",
            "p_value",
            "F_stat",
            "weak_iv_flag",
            "sign_agreement",
            "persistence_agreement",
            "turning_point_difference",
            "cumulative_direction_match",
            "IV_vs_OLS_ratio",
            "iv_cumulative",
            "ols_cumulative",
            "iv_cumulative_sign",
            "ols_cumulative_sign",
            "nobs_x",
        ]
    ].rename(columns={"beta": "lpiv_beta", "HAC_se": "lpiv_HAC_se", "p_value": "lpiv_p_value", "nobs_x": "nobs"})


def baseline_ar_inference(data: pd.DataFrame, spec, iv: pd.DataFrame, ols: pd.DataFrame) -> pd.DataFrame:
    ols_lookup = ols.set_index(["response", "horizon"])
    rows: list[dict[str, object]] = []
    for _, iv_row in iv.iterrows():
        response = iv_row["response"]
        horizon = int(iv_row["horizon"])
        frame, outcome, control_columns = complete_horizon_frame(
            data,
            response=response,
            horizon=horizon,
            controls=spec.resolved_control_variables(),
            control_lags=spec.control_lags,
            required_current=[spec.endogenous_policy, spec.instrument],
        )
        ar = ar_confidence_interval(
            frame[outcome],
            frame[spec.endogenous_policy],
            frame[spec.instrument].rename(spec.instrument),
            frame[control_columns],
            beta_hat=float(iv_row["beta"]),
            beta_se=float(iv_row["HAC_se"]),
            ols_beta=float(ols_lookup.loc[(response, horizon), "ols_beta"]),
            hac_bandwidth=hac_bandwidth_for_horizon(horizon),
        )
        rows.append(
            {
                "response": response,
                "horizon": horizon,
                "beta": float(iv_row["beta"]),
                "F_stat": float(iv_row["F_stat"]),
                "partial_R2": float(iv_row["partial_R2"]),
                "AR_stat": ar.statistic,
                "AR_p_value": ar.p_value,
                "AR_CI_lower": ar.ci_lower,
                "AR_CI_upper": ar.ci_upper,
                "AR_CI_bounded": ar.bounded,
                "AR_reject": ar.reject,
                "weak_iv_flag": iv_row["weak_iv_flag"],
                "nobs": int(iv_row["nobs"]),
            }
        )
    return pd.DataFrame(rows)


def directional_support_table(
    iv: pd.DataFrame,
    ols: pd.DataFrame,
    dax: pd.DataFrame,
    lags: pd.DataFrame,
    cumulative: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    ols_lookup = ols.set_index(["response", "horizon"])
    dax_lookup = dax.set_index(["response", "horizon"]) if not dax.empty else pd.DataFrame()
    cumulative_lookup = cumulative.set_index(["response", "horizon"])
    for _, row in iv.iterrows():
        response = row["response"]
        horizon = int(row["horizon"])
        base_sign = signed(row["beta"])
        signs = {"baseline": base_sign}
        if (response, horizon) in ols_lookup.index:
            signs["ols"] = signed(ols_lookup.loc[(response, horizon), "ols_beta"])
        if not dax_lookup.empty and (response, horizon) in dax_lookup.index:
            signs["dax"] = signed(dax_lookup.loc[(response, horizon), "dax_augmented_beta"])
        lag_subset = lags.loc[lags["response"].eq(response) & lags["horizon"].eq(horizon)]
        for _, lag_row in lag_subset.iterrows():
            signs[f"lag_{int(lag_row['control_lags'])}"] = signed(lag_row["beta"])
        if (response, horizon) in cumulative_lookup.index:
            signs["cumulative"] = signed(cumulative_lookup.loc[(response, horizon), "cumulative_response"])
        comparable = {k: v for k, v in signs.items() if k != "baseline" and v != 0 and base_sign != 0}
        agreement = [v == base_sign for v in comparable.values()]
        score = float(np.mean(agreement)) if agreement else np.nan
        rows.append(
            {
                "response": response,
                "horizon": horizon,
                "baseline_sign": sign_label(row["beta"]),
                "directional_stability_score": score,
                "supporting_sources": ",".join(k for k, v in comparable.items() if v == base_sign),
                "conflicting_sources": ",".join(k for k, v in comparable.items() if v != base_sign),
                "source_count": len(comparable),
            }
        )
    return pd.DataFrame(rows)


def classify_weak_iv_cells(ar: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
    merged = ar.merge(support, on=["response", "horizon"], how="left")

    def classify(row: pd.Series) -> str:
        ar_clean = bool(row["AR_reject"]) and bool(row["AR_CI_bounded"]) and not (
            row["AR_CI_lower"] <= 0.0 <= row["AR_CI_upper"]
        )
        if ar_clean:
            return "robust_signal"
        if not pd.isna(row["directional_stability_score"]) and row["directional_stability_score"] >= 0.60:
            return "directional_only"
        return "unidentified"

    merged["weak_iv_robust_status"] = merged.apply(classify, axis=1)
    return merged


def _configure_axis(ax: plt.Axes) -> None:
    ax.axhline(0.0, color="#111827", linewidth=0.9)
    ax.grid(True, axis="y", color="#e5e7eb", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_ar_encoded_irf(classified: pd.DataFrame, response: str) -> None:
    subset = classified.loc[classified["response"].eq(response)].sort_values("horizon")
    if subset.empty:
        return
    x = subset["horizon"].to_numpy(dtype=float)
    y = subset["beta"].to_numpy(dtype=float)
    lower = subset["AR_CI_lower"].replace([-np.inf, np.inf], np.nan).to_numpy(dtype=float)
    upper = subset["AR_CI_upper"].replace([-np.inf, np.inf], np.nan).to_numpy(dtype=float)
    bounded = subset["AR_CI_bounded"].fillna(False).to_numpy(dtype=bool)

    fig, ax = plt.subplots(figsize=(7.3, 4.5))
    if bounded.any():
        ax.fill_between(
            x[bounded],
            lower[bounded],
            upper[bounded],
            color="#93c5fd",
            alpha=0.24,
            label="AR 90% CI",
        )
    if (~bounded).any():
        finite_y = y[np.isfinite(y)]
        spread = max(np.nanmax(np.abs(finite_y)) * 1.8, 1e-10) if finite_y.size else 1e-10
        ax.fill_between(
            x[~bounded],
            -spread,
            spread,
            color="#cbd5e1",
            alpha=0.22,
            hatch="//",
            edgecolor="#94a3b8",
            label="AR inconclusive/unbounded",
        )
    for status, marker, color, label in [
        ("robust_signal", "o", "#111827", "robust signal"),
        ("directional_only", "o", "#64748b", "directional only"),
        ("unidentified", "x", "#b91c1c", "unidentified"),
    ]:
        mask = subset["weak_iv_robust_status"].eq(status).to_numpy()
        if mask.any():
            ax.scatter(x[mask], y[mask], marker=marker, s=58, color=color, label=label, zorder=4)
    weak_first_stage = subset["F_stat"].lt(5.0).to_numpy()
    if weak_first_stage.any():
        ax.scatter(
            x[weak_first_stage],
            y[weak_first_stage],
            marker="x",
            s=82,
            color="#b91c1c",
            linewidths=1.8,
            label="F < 5",
            zorder=5,
        )
    ax.plot(x, y, color="#475569", linewidth=1.3, linestyle="--")
    _configure_axis(ax)
    ax.set_xticks(list(DEFAULT_HORIZONS))
    ax.set_xlabel("Horizon")
    ax.set_ylabel("Response")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    ax.set_title(f"Weak-IV robust LP-IV encoding: {RESPONSE_LABELS.get(response, response)}", loc="left")
    ax.legend(loc="best", frameon=False, fontsize=8)
    fig.text(0.01, 0.01, "Red/x markers indicate F < 5 or no stable weak-IV robust signal.", fontsize=7.5, color="#475569")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(WEAK_PLOT_DIR / f"ar_encoded_irf_{response}.png", dpi=220)
    fig.savefig(WEAK_PLOT_DIR / f"ar_encoded_irf_{response}.svg")
    fig.savefig(WEAK_BASELINE_DIR / f"ar_encoded_irf_{response}.png", dpi=220)
    fig.savefig(WEAK_BASELINE_DIR / f"ar_encoded_irf_{response}.svg")
    plt.close(fig)


def plot_ols_overlay(comparison: pd.DataFrame, response: str) -> None:
    subset = comparison.loc[comparison["response"].eq(response)].sort_values("horizon")
    if subset.empty:
        return
    fig, ax = plt.subplots(figsize=(7.1, 4.2))
    ax.plot(subset["horizon"], subset["ols_beta"], marker="s", linewidth=2.0, label="OLS LP")
    ax.plot(subset["horizon"], subset["lpiv_beta"], marker="o", linewidth=2.0, label="LP-IV")
    weak = subset["weak_iv_flag"].eq("weak_iv_risk").to_numpy()
    if weak.any():
        ax.scatter(
            subset.loc[weak, "horizon"],
            subset.loc[weak, "lpiv_beta"],
            marker="x",
            s=58,
            color="#b91c1c",
            linewidths=1.8,
            label="LP-IV F < 5",
            zorder=5,
        )
    _configure_axis(ax)
    ax.set_xticks(list(DEFAULT_HORIZONS))
    ax.set_xlabel("Horizon")
    ax.set_ylabel("Response")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    ax.set_title(f"OLS vs LP-IV: {RESPONSE_LABELS.get(response, response)}", loc="left")
    ax.legend(loc="best", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OLS_PLOT_DIR / f"ols_vs_lpiv_{response}.png", dpi=220)
    fig.savefig(OLS_PLOT_DIR / f"ols_vs_lpiv_{response}.svg")
    plt.close(fig)


def persistence_metrics(table: pd.DataFrame, value_col: str, dimension: str) -> pd.DataFrame:
    rows = []
    for response, subset in table.groupby("response"):
        ordered = subset.sort_values("horizon")
        values = ordered[value_col].astype(float)
        signs = values.map(signed)
        positive_count = int((signs > 0).sum())
        negative_count = int((signs < 0).sum())
        nonzero = [(int(h), int(s)) for h, s in zip(ordered["horizon"], signs) if s != 0]
        sign_flip = np.nan
        if nonzero:
            first_sign = nonzero[0][1]
            for horizon, sign in nonzero[1:]:
                if sign != first_sign:
                    sign_flip = horizon
                    break
        cumulative = float(values.sum())
        weights = ordered["horizon"].astype(float) + 1.0
        persistence_score = float((np.sign(values) * weights).sum() / weights.sum())
        rows.append(
            {
                "dimension": dimension,
                "response": response,
                "positive_horizon_count": positive_count,
                "negative_horizon_count": negative_count,
                "sign_flip_horizon": sign_flip,
                "cumulative_response": cumulative,
                "cumulative_sign": sign_label(cumulative),
                "persistence_score": persistence_score,
            }
        )
    return pd.DataFrame(rows)


def build_sign_stability_matrix(
    iv: pd.DataFrame,
    ols: pd.DataFrame,
    dax: pd.DataFrame,
    lags: pd.DataFrame,
    cumulative: pd.DataFrame,
    regime: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def add_rows(frame: pd.DataFrame, dimension: str, value_col: str, extra_cols: list[str] | None = None) -> None:
        extra_cols = extra_cols or []
        for _, row in frame.iterrows():
            out = {
                "dimension": dimension,
                "response": row["response"],
                "horizon": int(row["horizon"]),
                "value": float(row[value_col]),
                "sign": sign_label(float(row[value_col])),
            }
            for col in extra_cols:
                out[col] = row[col]
            rows.append(out)

    add_rows(iv, "baseline_lpiv", "beta")
    add_rows(ols.rename(columns={"ols_beta": "beta"}), "ols_lp", "beta")
    if not dax.empty:
        add_rows(dax.rename(columns={"dax_augmented_beta": "beta"}), "dax_robustness", "beta")
    add_rows(lags, "lag_sensitivity", "beta", ["control_lags"])
    add_rows(cumulative.rename(columns={"cumulative_response": "beta"}), "cumulative_irf", "beta")
    if not regime.empty:
        add_rows(regime.rename(columns={"beta": "beta"}), "regime_interactions", "beta", ["regime"])
    return pd.DataFrame(rows)


def directional_consistency(sign_matrix: pd.DataFrame, classified: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for response in BASELINE_RESPONSES:
        for horizon in DEFAULT_HORIZONS:
            subset = sign_matrix.loc[sign_matrix["response"].eq(response) & sign_matrix["horizon"].eq(horizon)]
            nonzero = subset.loc[subset["sign"].ne("zero")]
            if nonzero.empty:
                majority_sign = "zero"
                majority_share = np.nan
            else:
                counts = nonzero["sign"].value_counts()
                majority_sign = counts.idxmax()
                majority_share = float(counts.max() / counts.sum())
            status = classified.loc[
                classified["response"].eq(response) & classified["horizon"].eq(horizon), "weak_iv_robust_status"
            ]
            rows.append(
                {
                    "response": response,
                    "horizon": horizon,
                    "majority_sign": majority_sign,
                    "majority_share": majority_share,
                    "positive_count": int((subset["sign"] == "positive").sum()),
                    "negative_count": int((subset["sign"] == "negative").sum()),
                    "zero_count": int((subset["sign"] == "zero").sum()),
                    "weak_iv_robust_status": status.iloc[0] if not status.empty else "missing",
                }
            )
    return pd.DataFrame(rows)


def structural_ranking(
    sign_matrix: pd.DataFrame,
    persistence: pd.DataFrame,
    classified: pd.DataFrame,
    regime_comparison: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for response in BASELINE_RESPONSES:
        signs = sign_matrix.loc[sign_matrix["response"].eq(response) & sign_matrix["sign"].ne("zero")]
        if signs.empty:
            majority_sign = "zero"
            stability = np.nan
        else:
            counts = signs["sign"].value_counts()
            majority_sign = counts.idxmax()
            stability = float(counts.max() / counts.sum())
        base_persistence = persistence.loc[
            persistence["dimension"].eq("baseline_lpiv") & persistence["response"].eq(response)
        ]
        persistence_score = float(base_persistence["persistence_score"].iloc[0]) if not base_persistence.empty else np.nan
        cumulative_sign = base_persistence["cumulative_sign"].iloc[0] if not base_persistence.empty else "missing"
        robust_counts = classified.loc[classified["response"].eq(response), "weak_iv_robust_status"].value_counts()
        if robust_counts.get("robust_signal", 0) > 0:
            weak_status = "some_robust_signal"
        elif robust_counts.get("directional_only", 0) > 0:
            weak_status = "directional_only"
        else:
            weak_status = "unidentified"
        regime_subset = regime_comparison.loc[regime_comparison["response"].eq(response)]
        if regime_subset.empty:
            regime_consistency = np.nan
        else:
            regime_signs = regime_subset["cumulative"].map(sign_label)
            regime_consistency = float((regime_signs == majority_sign).mean()) if majority_sign != "zero" else np.nan
        score = (
            (0.35 * (0.0 if pd.isna(stability) else stability))
            + (0.25 * abs(0.0 if pd.isna(persistence_score) else persistence_score))
            + (0.20 * (0.0 if pd.isna(regime_consistency) else regime_consistency))
            + (0.20 * (1.0 if weak_status == "some_robust_signal" else 0.5 if weak_status == "directional_only" else 0.0))
        )
        rows.append(
            {
                "channel": CHANNEL_NAMES[response],
                "response": response,
                "Direction": majority_sign,
                "Persistence": persistence_score,
                "Stability": stability,
                "Regime_consistency": regime_consistency,
                "Weak_IV_status": weak_status,
                "ranking_score": score,
                "cumulative_sign": cumulative_sign,
            }
        )
    return pd.DataFrame(rows).sort_values("ranking_score", ascending=False)


def regime_ar_diagnostics(data: pd.DataFrame, spec, iv_regime: pd.DataFrame) -> pd.DataFrame:
    rows = []
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
            for regime in REGIME_NAMES:
                subset = frame.loc[frame["lpiv_regime"].eq(regime)].copy()
                required_nobs = len(control_columns) + 5
                row_base = {
                    "response": response,
                    "horizon": horizon,
                    "regime": regime,
                    "nobs": int(subset.dropna(subset=[outcome, spec.endogenous_policy, spec.instrument]).shape[0]),
                    "AR_p_value": np.nan,
                    "AR_CI_lower": np.nan,
                    "AR_CI_upper": np.nan,
                    "AR_reject": False,
                    "weak_iv_robust_status": "not_feasible",
                }
                if row_base["nobs"] < required_nobs or subset[spec.instrument].nunique(dropna=True) < 3:
                    rows.append(row_base)
                    continue
                regime_beta = iv_regime.loc[
                    iv_regime["response"].eq(response)
                    & iv_regime["horizon"].eq(horizon)
                    & iv_regime["regime"].eq(regime),
                    "beta",
                ]
                beta_hat = float(regime_beta.iloc[0]) if not regime_beta.empty else 0.0
                ols_beta = 0.0
                try:
                    ar = ar_confidence_interval(
                        subset[outcome],
                        subset[spec.endogenous_policy],
                        subset[spec.instrument].rename(spec.instrument),
                        subset[control_columns],
                        beta_hat=beta_hat,
                        beta_se=max(abs(beta_hat), 1e-10),
                        ols_beta=ols_beta,
                        hac_bandwidth=hac_bandwidth_for_horizon(horizon),
                        grid_points=401,
                    )
                    row_base.update(
                        {
                            "AR_p_value": ar.p_value,
                            "AR_CI_lower": ar.ci_lower,
                            "AR_CI_upper": ar.ci_upper,
                            "AR_reject": ar.reject,
                            "weak_iv_robust_status": "robust_signal"
                            if ar.reject and ar.bounded and not (ar.ci_lower <= 0 <= ar.ci_upper)
                            else "directional_only"
                            if not ar.reject
                            else "unidentified",
                        }
                    )
                except (ValueError, np.linalg.LinAlgError):
                    row_base["weak_iv_robust_status"] = "not_feasible"
                rows.append(row_base)
    return pd.DataFrame(rows)


def regime_mutation_table(regime_comparison: pd.DataFrame, regime_ar: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in regime_comparison.iterrows():
        ar_subset = regime_ar.loc[
            regime_ar["response"].eq(row["response"]) & regime_ar["regime"].eq(row["regime"])
        ]
        statuses = ar_subset["weak_iv_robust_status"].value_counts() if not ar_subset.empty else pd.Series(dtype=int)
        if statuses.get("robust_signal", 0) > 0:
            ar_status = "some_robust_signal"
        elif statuses.get("directional_only", 0) > 0:
            ar_status = "directional_only"
        elif statuses.get("not_feasible", 0) == len(ar_subset) and not ar_subset.empty:
            ar_status = "not_feasible"
        else:
            ar_status = "unidentified"
        rows.append(
            {
                "regime": row["regime"],
                "response": row["response"],
                "peak_response": row["peak"],
                "peak_horizon": row["peak_horizon"],
                "cumulative_response": row["cumulative"],
                "sign_persistence": row["persistence"],
                "first_stage_strength": row["min_F_stat"],
                "weak_iv_flag": row["weak_iv_flag"],
                "AR_robustness_status": ar_status,
            }
        )
    return pd.DataFrame(rows)


def write_method_note() -> None:
    note = """# Weak-IV Robustification Method Note

This validation layer preserves the frozen baseline LP-IV specification.

Anderson-Rubin tests are implemented by testing beta0 in:

`y_{t+h} - y_{t-1} - beta0 * d_ecb_assets_ea_qavg_t`

on the frozen external instrument and frozen two-lag controls, using the same Newey-West bandwidth rule as the baseline LP-IV.

The reported AR p-value tests `beta0 = 0`. The AR confidence interval is a grid inversion of the 10 percent AR test. Unbounded intervals are reported as `-inf` or `inf` and interpreted as weak-IV inconclusive.

Cell classification:

- `robust_signal`: AR rejects zero and the inverted AR interval is bounded and excludes zero
- `directional_only`: AR is inconclusive, but the sign is stable across controlled comparison layers
- `unidentified`: neither weak-IV robust rejection nor directional stability is present

Regime AR diagnostics are reported only where feasible. Short regime subsamples, especially COVID and baseline-window tightening, are flagged as not feasible rather than forced into false precision.
"""
    (WEAK_ROOT / "weak_iv_method_note.md").write_text(note, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    spec = baseline_specification(name="weak_iv_robust_baseline", output_subdir="weak_iv_robust")
    data = prepare_lpiv_dataset(spec)
    validate_specification_data(data, spec)

    iv = canonicalize_table(results_to_frame(estimate_specification(spec, data=data)))
    ols = estimate_ols(data, spec)
    ols_comparison = structural_ols_comparison(iv, ols)

    dax = pd.read_csv(DAX_DIR / "baseline_vs_dax_augmented_comparison.csv")
    lags = pd.read_csv(RESULTS_ROOT / "weak_iv_validation" / "lag_robustness_1_2_4.csv")
    cumulative = pd.read_csv(CUMULATIVE_DIR / "cumulative_irf_summary_table.csv")
    regime = pd.read_csv(REGIME_DIR / "regime_irf_summary_table.csv")
    regime_comparison = pd.read_csv(REGIME_DIR / "regime_comparison_table.csv")

    ar = baseline_ar_inference(data, spec, iv, ols)
    support = directional_support_table(iv, ols, dax, lags, cumulative)
    classified = classify_weak_iv_cells(ar, support)

    iv.to_csv(WEAK_BASELINE_DIR / "baseline_lpiv_coefficients.csv", index=False)
    ar.to_csv(WEAK_BASELINE_DIR / "baseline_ar_inference.csv", index=False)
    classified.to_csv(WEAK_TABLE_DIR / "weak_iv_classification.csv", index=False)
    classified.to_csv(WEAK_BASELINE_DIR / "baseline_weak_iv_classification.csv", index=False)

    ols.to_csv(OLS_TABLE_DIR / "ols_lp_coefficients.csv", index=False)
    ols_comparison.to_csv(OLS_TABLE_DIR / "ols_vs_lpiv_structural_comparison.csv", index=False)
    ols_comparison.to_csv(OLS_DIAG_DIR / "structural_comparison_diagnostics.csv", index=False)

    for response in BASELINE_RESPONSES:
        plot_ar_encoded_irf(classified, response)
    for response in [
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
    ]:
        plot_ols_overlay(ols_comparison, response)

    regime_ar = regime_ar_diagnostics(data, spec, regime)
    regime_ar.to_csv(WEAK_REGIME_DIR / "regime_ar_diagnostics.csv", index=False)
    mutation = regime_mutation_table(regime_comparison, regime_ar)
    mutation.to_csv(REGIME_DIR / "regime_mutation_table.csv", index=False)
    mutation.to_csv(WEAK_REGIME_DIR / "regime_mutation_table.csv", index=False)

    sign_matrix = build_sign_stability_matrix(iv, ols, dax, lags, cumulative, regime)
    sign_matrix.to_csv(STABILITY_ROOT / "sign_stability_matrix.csv", index=False)
    consistency = directional_consistency(sign_matrix, classified)
    consistency.to_csv(STABILITY_ROOT / "directional_consistency.csv", index=False)

    persistence_frames = [
        persistence_metrics(iv, "beta", "baseline_lpiv"),
        persistence_metrics(ols.rename(columns={"ols_beta": "beta"}), "beta", "ols_lp"),
        persistence_metrics(dax.rename(columns={"dax_augmented_beta": "beta"}), "beta", "dax_robustness"),
    ]
    for lag_count, subset in lags.groupby("control_lags"):
        persistence_frames.append(persistence_metrics(subset, "beta", f"lag_{int(lag_count)}"))
    persistence = pd.concat(persistence_frames, ignore_index=True)
    persistence.to_csv(STABILITY_ROOT / "persistence_consistency.csv", index=False)

    ranking = structural_ranking(sign_matrix, persistence, classified, regime_comparison)
    ranking.to_csv(STABILITY_ROOT / "transmission_ranking.csv", index=False)
    ranking.to_csv(WEAK_TABLE_DIR / "final_transmission_ranking.csv", index=False)

    # Keep the full-window regime check visible for the tightening period.
    full_regime_spec = baseline_specification(
        name="regime_full_window_robustness_only",
        sample=ROBUSTNESS_SAMPLE,
        output_subdir="weak_iv_robust",
    )
    full_data = prepare_lpiv_dataset(full_regime_spec)
    full_regime_ar = regime_ar_diagnostics(full_data, full_regime_spec, regime)
    full_regime_ar.to_csv(WEAK_REGIME_DIR / "regime_full_window_robustness_ar_diagnostics.csv", index=False)

    write_method_note()
    print("Weak-IV robustification complete.")
    print(f"Baseline cells classified: {classified.shape[0]}")
    print(classified["weak_iv_robust_status"].value_counts().to_string())


if __name__ == "__main__":
    main()
