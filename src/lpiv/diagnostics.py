from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd

from .first_stage import estimate_first_stage
from .horizon_design import add_lagged_controls, complete_horizon_frame
from .inference import RegressionResult
from .specifications import LPIVSpecification, REGIME_NAMES, RESULTS_ROOT, prepare_lpiv_dataset, validate_specification_data


def autocorrelation(series: pd.Series, lags: Iterable[int] = (1, 2, 4, 8)) -> dict[str, float]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    output: dict[str, float] = {}
    for lag in lags:
        output[f"residual_autocorr_lag_{lag}"] = float(values.autocorr(lag=lag)) if values.shape[0] > lag else np.nan
    return output


def leverage_values(result: RegressionResult) -> pd.Series:
    design = result.x.apply(pd.to_numeric, errors="coerce").astype(float)
    x = design.to_numpy(dtype=float)
    hat = np.sum((x @ np.linalg.pinv(x.T @ x)) * x, axis=1)
    return pd.Series(hat, index=design.index, name="leverage")


def breusch_pagan_statistic(result: RegressionResult) -> float:
    residual_sq = result.residuals**2
    design = result.x.drop(columns=["const"], errors="ignore")
    if design.empty:
        return np.nan
    joined = pd.concat([residual_sq.rename("_e2"), design], axis=1).dropna()
    if joined.shape[0] <= joined.shape[1] + 1:
        return np.nan
    y = joined["_e2"].to_numpy(dtype=float)
    x = joined.drop(columns=["_e2"]).to_numpy(dtype=float)
    x = np.column_stack([np.ones(x.shape[0]), x])
    beta = np.linalg.pinv(x.T @ x) @ x.T @ y
    fitted = x @ beta
    tss = np.sum((y - y.mean()) ** 2)
    if math.isclose(float(tss), 0.0):
        return np.nan
    r2 = 1.0 - np.sum((y - fitted) ** 2) / tss
    return float(joined.shape[0] * max(0.0, r2))


def jarque_bera_statistic(residuals: pd.Series) -> float:
    values = pd.to_numeric(residuals, errors="coerce").dropna()
    nobs = values.shape[0]
    if nobs < 8:
        return np.nan
    centered = values - values.mean()
    std = centered.std(ddof=0)
    if math.isclose(float(std), 0.0):
        return np.nan
    skewness = float(((centered / std) ** 3).mean())
    kurtosis = float(((centered / std) ** 4).mean())
    return float(nobs / 6.0 * (skewness**2 + ((kurtosis - 3.0) ** 2) / 4.0))


def residual_diagnostics(result: RegressionResult) -> dict[str, float]:
    residuals = result.residuals
    leverage = leverage_values(result)
    resid_std = residuals.std(ddof=1)
    standardized = residuals / resid_std if not math.isclose(float(resid_std), 0.0) else residuals * np.nan
    cooks = (standardized**2 * leverage) / ((1.0 - leverage).replace(0.0, np.nan) ** 2 * max(result.x.shape[1], 1))
    output = {
        "residual_mean": float(residuals.mean()),
        "residual_std": float(residuals.std(ddof=1)),
        "jarque_bera_stat": jarque_bera_statistic(residuals),
        "breusch_pagan_lm_stat": breusch_pagan_statistic(result),
        "max_leverage": float(leverage.max()),
        "mean_leverage": float(leverage.mean()),
        "max_abs_standardized_residual": float(standardized.abs().max()),
        "outlier_count_abs_std_gt_2": int((standardized.abs() > 2.0).sum()),
        "max_cooks_distance": float(cooks.max()),
    }
    output.update(autocorrelation(residuals))
    return output


def residual_diagnostics_frame(results: Iterable[object]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in results:
        result = getattr(item, "iv_result")
        row: dict[str, object] = {
            "specification": item.specification.name,
            "response": item.response,
            "horizon": item.horizon,
            "nobs": result.nobs,
            "hac_bandwidth": result.hac_bandwidth,
        }
        row.update(residual_diagnostics(result))
        rows.append(row)
    return pd.DataFrame(rows)


def horizon_specific_first_stage_quality(data: pd.DataFrame, spec: LPIVSpecification) -> pd.DataFrame:
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
            fs = estimate_first_stage(
                frame.dropna(subset=[outcome]),
                policy_variable=spec.endogenous_policy,
                instruments=spec.instrument,
                controls=control_columns,
                hac_bandwidth=max(1, horizon + 1),
            )
            row = fs.to_row()
            row.update({"response": response, "horizon": horizon, "outcome": outcome})
            rows.append(row)
    return pd.DataFrame(rows)


def identification_contribution(data: pd.DataFrame, spec: LPIVSpecification) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame, control_columns = add_lagged_controls(data, spec.resolved_control_variables(), spec.control_lags)
    required = [spec.endogenous_policy, spec.instrument, *control_columns, "lpiv_regime"]
    clean = frame.dropna(subset=required).copy()
    fs = estimate_first_stage(
        clean,
        policy_variable=spec.endogenous_policy,
        instruments=spec.instrument,
        controls=control_columns,
        hac_bandwidth=1,
    )
    clean["instrument_variance_component"] = clean[spec.instrument] ** 2
    clean["policy_variance_component"] = clean[spec.endogenous_policy] ** 2
    clean["first_stage_signal_component"] = fs.result.fitted_values.reindex(clean.index) ** 2

    total_instrument = clean["instrument_variance_component"].sum()
    total_policy = clean["policy_variance_component"].sum()
    total_signal = clean["first_stage_signal_component"].sum()
    regime = (
        clean.groupby("lpiv_regime", as_index=False)
        .agg(
            observations=("date", "count"),
            instrument_variance_component=("instrument_variance_component", "sum"),
            policy_variance_component=("policy_variance_component", "sum"),
            first_stage_signal_component=("first_stage_signal_component", "sum"),
        )
        .sort_values("instrument_variance_component", ascending=False)
    )
    regime["instrument_variance_share"] = regime["instrument_variance_component"] / total_instrument
    regime["policy_variance_share"] = regime["policy_variance_component"] / total_policy
    regime["first_stage_signal_share"] = regime["first_stage_signal_component"] / total_signal

    quarter = clean[
        [
            "date",
            "quarter",
            "lpiv_regime",
            spec.instrument,
            spec.endogenous_policy,
            "instrument_variance_component",
            "policy_variance_component",
            "first_stage_signal_component",
        ]
    ].copy()
    quarter["instrument_variance_share"] = quarter["instrument_variance_component"] / total_instrument
    quarter["policy_variance_share"] = quarter["policy_variance_component"] / total_policy
    quarter["first_stage_signal_share"] = quarter["first_stage_signal_component"] / total_signal
    quarter = quarter.sort_values("instrument_variance_share", ascending=False)
    return regime, quarter


def rolling_lpiv_coefficients(
    data: pd.DataFrame,
    spec: LPIVSpecification,
    window: int = 32,
    min_obs: int = 24,
) -> pd.DataFrame:
    from .local_projection_iv import estimate_lpiv_horizon

    rows: list[dict[str, object]] = []
    clean = data.reset_index(drop=True)
    for end in range(window, clean.shape[0] + 1):
        subset = clean.iloc[end - window : end].copy()
        if subset.shape[0] < min_obs:
            continue
        for response in spec.responses:
            for horizon in spec.horizons:
                try:
                    result = estimate_lpiv_horizon(subset, spec, response, horizon)
                except (ValueError, np.linalg.LinAlgError):
                    continue
                row = result.to_row()
                row.update(
                    {
                        "rolling_window": window,
                        "rolling_start": subset["quarter"].iloc[0],
                        "rolling_end": subset["quarter"].iloc[-1],
                    }
                )
                rows.append(row)
    return pd.DataFrame(rows)


def write_diagnostics_outputs(
    results: Iterable[object],
    spec: LPIVSpecification,
    data: pd.DataFrame | None = None,
) -> None:
    frame = data.copy() if data is not None else prepare_lpiv_dataset(spec)
    validate_specification_data(frame, spec)
    target = RESULTS_ROOT / "diagnostics"
    target.mkdir(parents=True, exist_ok=True)
    residuals = residual_diagnostics_frame(results)
    first_stage = horizon_specific_first_stage_quality(frame, spec)
    regime, quarter = identification_contribution(frame, spec)
    rolling = rolling_lpiv_coefficients(frame, spec)

    residuals.to_csv(target / f"{spec.name}_residual_diagnostics.csv", index=False)
    first_stage.to_csv(target / f"{spec.name}_horizon_first_stage_quality.csv", index=False)
    regime.to_csv(target / f"{spec.name}_regime_contribution.csv", index=False)
    quarter.to_csv(target / f"{spec.name}_quarter_contribution.csv", index=False)
    rolling.to_csv(target / f"{spec.name}_rolling_lpiv_coefficients.csv", index=False)

    lines = [
        f"# LP-IV Checks: {spec.name}",
        "",
        "These files should be reviewed before interpreting the response estimates.",
        "",
        f"- Residual diagnostic rows: {residuals.shape[0]}",
        f"- Horizon-specific first-stage rows: {first_stage.shape[0]}",
        f"- Regime contribution rows: {regime.shape[0]}",
        f"- Quarter contribution rows: {quarter.shape[0]}",
        f"- Rolling coefficient rows: {rolling.shape[0]}",
    ]
    (target / f"{spec.name}_diagnostics_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
