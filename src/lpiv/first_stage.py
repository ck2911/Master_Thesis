from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .inference import RegressionResult, fit_ols, hac_bandwidth_for_horizon
from .specifications import REGIME_NAMES, RESULTS_ROOT


@dataclass
class FirstStageResult:
    policy_variable: str
    instruments: tuple[str, ...]
    controls: tuple[str, ...]
    result: RegressionResult
    restricted_result: RegressionResult
    f_statistic: float
    partial_r_squared: float
    sample_start: str
    sample_end: str

    @property
    def nobs(self) -> int:
        return self.result.nobs

    def to_row(self) -> dict[str, object]:
        coefficient = self.instruments[0] if len(self.instruments) == 1 else ""
        row = {
            "policy_variable": self.policy_variable,
            "instrument": ",".join(self.instruments),
            "nobs": self.nobs,
            "sample_start": self.sample_start,
            "sample_end": self.sample_end,
            "first_stage_f_stat": self.f_statistic,
            "partial_r_squared": self.partial_r_squared,
            "r_squared": self.result.r_squared,
            "hac_bandwidth": self.result.hac_bandwidth,
        }
        if coefficient and coefficient in self.result.coefficients.index:
            row.update(
                {
                    "instrument_coefficient": float(self.result.coefficients[coefficient]),
                    "instrument_std_error": float(self.result.std_errors[coefficient]),
                    "instrument_t_stat": float(self.result.t_statistics[coefficient]),
                    "instrument_p_value": float(self.result.p_values[coefficient]),
                }
            )
        return row


def estimate_first_stage(
    data: pd.DataFrame,
    policy_variable: str,
    instruments: str | Iterable[str],
    controls: Iterable[str],
    hac_bandwidth: int = 1,
) -> FirstStageResult:
    instrument_columns = (instruments,) if isinstance(instruments, str) else tuple(instruments)
    control_columns = tuple(controls)
    required = [policy_variable, *instrument_columns, *control_columns]
    clean = data.dropna(subset=required).copy()
    if clean.empty:
        raise ValueError("No complete observations available for first-stage estimation.")

    full_x = clean[[*control_columns, *instrument_columns]]
    restricted_x = clean[list(control_columns)]
    y = clean[policy_variable]
    full = fit_ols(y, full_x, hac_bandwidth=hac_bandwidth, method="first_stage_ols_hac")
    restricted = fit_ols(y, restricted_x, hac_bandwidth=hac_bandwidth, method="first_stage_restricted_ols_hac")
    f_stat, partial_r2 = partial_f_statistic(y, full, restricted, q=len(instrument_columns))
    return FirstStageResult(
        policy_variable=policy_variable,
        instruments=instrument_columns,
        controls=control_columns,
        result=full,
        restricted_result=restricted,
        f_statistic=f_stat,
        partial_r_squared=partial_r2,
        sample_start=str(clean["quarter"].min()) if "quarter" in clean else "",
        sample_end=str(clean["quarter"].max()) if "quarter" in clean else "",
    )


def partial_f_statistic(
    y: pd.Series,
    unrestricted: RegressionResult,
    restricted: RegressionResult,
    q: int,
) -> tuple[float, float]:
    unrestricted_rss = float((unrestricted.residuals**2).sum())
    restricted_rss = float((restricted.residuals**2).sum())
    if restricted_rss <= 0 or unrestricted.df_resid <= 0 or q <= 0:
        return np.nan, np.nan
    improvement = max(0.0, restricted_rss - unrestricted_rss)
    partial_r2 = max(0.0, min(1.0, improvement / restricted_rss))
    numerator = improvement / q
    denominator = unrestricted_rss / unrestricted.df_resid
    f_stat = np.nan if denominator <= 0 else numerator / denominator
    return float(f_stat), float(partial_r2)


def horizon_first_stage(
    data: pd.DataFrame,
    outcome: str,
    policy_variable: str,
    instrument: str,
    controls: Iterable[str],
    horizon: int,
) -> FirstStageResult:
    clean = data.dropna(subset=[outcome]).copy()
    return estimate_first_stage(
        clean,
        policy_variable=policy_variable,
        instruments=instrument,
        controls=controls,
        hac_bandwidth=hac_bandwidth_for_horizon(horizon),
    )


def rolling_relevance(
    data: pd.DataFrame,
    policy_variable: str,
    instrument: str,
    controls: Iterable[str],
    window: int = 28,
    min_obs: int = 20,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    required = [policy_variable, instrument, *controls]
    clean = data.dropna(subset=required).reset_index(drop=True)
    for end in range(window, clean.shape[0] + 1):
        sample = clean.iloc[end - window : end].copy()
        if sample.shape[0] < min_obs:
            continue
        try:
            result = estimate_first_stage(
                sample,
                policy_variable=policy_variable,
                instruments=instrument,
                controls=controls,
                hac_bandwidth=1,
            )
        except ValueError:
            continue
        row = result.to_row()
        row.update(
            {
                "window": window,
                "rolling_start": sample["quarter"].iloc[0] if "quarter" in sample else "",
                "rolling_end": sample["quarter"].iloc[-1] if "quarter" in sample else "",
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def regime_relevance(
    data: pd.DataFrame,
    policy_variable: str,
    instrument: str,
    controls: Iterable[str],
    min_obs: int = 8,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    control_columns = tuple(controls)
    required_nobs = max(min_obs, len(control_columns) + 4)
    for regime in REGIME_NAMES:
        subset = data.loc[data[f"regime_{regime}"].eq(1)].copy()
        if subset.dropna(subset=[policy_variable, instrument, *control_columns]).shape[0] < required_nobs:
            rows.append(
                {
                    "regime": regime,
                    "nobs": int(subset.dropna(subset=[policy_variable, instrument]).shape[0]),
                    "first_stage_f_stat": np.nan,
                    "partial_r_squared": np.nan,
                    "status": f"insufficient_regime_observations_for_{len(control_columns)}_controls",
                }
            )
            continue
        result = estimate_first_stage(
            subset,
            policy_variable=policy_variable,
            instruments=instrument,
            controls=control_columns,
            hac_bandwidth=1,
        )
        row = result.to_row()
        row["regime"] = regime
        row["status"] = "estimated"
        rows.append(row)
    return pd.DataFrame(rows)


def coefficient_stability(
    rolling: pd.DataFrame,
    coefficient_column: str = "instrument_coefficient",
) -> dict[str, float]:
    if rolling.empty or coefficient_column not in rolling.columns:
        return {"coefficient_mean": np.nan, "coefficient_std": np.nan, "sign_stability_share": np.nan}
    values = pd.to_numeric(rolling[coefficient_column], errors="coerce").dropna()
    if values.empty:
        return {"coefficient_mean": np.nan, "coefficient_std": np.nan, "sign_stability_share": np.nan}
    dominant_sign = np.sign(values.median())
    sign_share = np.nan if dominant_sign == 0 else float((np.sign(values) == dominant_sign).mean())
    return {
        "coefficient_mean": float(values.mean()),
        "coefficient_std": float(values.std(ddof=1)) if values.shape[0] > 1 else 0.0,
        "sign_stability_share": sign_share,
    }


def write_first_stage_outputs(
    baseline: FirstStageResult,
    rolling: pd.DataFrame,
    regime: pd.DataFrame,
    output_dir: Path | None = None,
    prefix: str = "baseline",
) -> None:
    target = output_dir or RESULTS_ROOT / "diagnostics" / "first_stage"
    target.mkdir(parents=True, exist_ok=True)
    baseline_table = pd.DataFrame([baseline.to_row()])
    baseline_table.to_csv(target / f"{prefix}_first_stage.csv", index=False)
    rolling.to_csv(target / f"{prefix}_rolling_first_stage.csv", index=False)
    regime.to_csv(target / f"{prefix}_regime_first_stage.csv", index=False)
    stability = coefficient_stability(rolling)
    pd.DataFrame([stability]).to_csv(target / f"{prefix}_coefficient_stability.csv", index=False)
    try:
        from .plotting import write_series_svg

        write_series_svg(
            baseline.result.residuals,
            target / f"{prefix}_first_stage_residuals.svg",
            title=f"{prefix} First-Stage Residuals",
            y_label="Residual",
        )
    except Exception:
        pass

    lines = [
        "# LP-IV First-Stage Check",
        "",
        "This checks instrument relevance and stability before interpreting response estimates.",
        "",
        f"- Policy variable: `{baseline.policy_variable}`",
        f"- Instrument: `{','.join(baseline.instruments)}`",
        f"- Observations: {baseline.nobs}",
        f"- First-stage F-statistic: {baseline.f_statistic:.3f}",
        f"- Partial R2: {baseline.partial_r_squared:.3f}",
    ]
    (target / f"{prefix}_first_stage_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if prefix == "baseline":
        baseline_table.to_csv(target / "baseline_first_stage.csv", index=False)
        rolling.to_csv(target / "rolling_first_stage.csv", index=False)
        regime.to_csv(target / "regime_first_stage.csv", index=False)
        pd.DataFrame([stability]).to_csv(target / "coefficient_stability.csv", index=False)
        (target / "first_stage_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
