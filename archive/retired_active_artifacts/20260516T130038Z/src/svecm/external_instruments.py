from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


@dataclass(frozen=True)
class InstrumentSpec:
    name: str
    date_column: str
    value_column: str
    frequency: str = "quarterly"
    expected_sign: str = "contractionary_positive"


def load_external_instrument(path: Path, spec: InstrumentSpec) -> pd.Series:
    """Load a future ECB monetary surprise series and return a dated Series.

    The final instrument is not yet present in the repository. This loader is a
    schema gate: it requires explicit date/value columns and refuses implicit
    non-ECB shock assumptions.
    """

    if not path.exists():
        raise FileNotFoundError(f"External instrument file does not exist: {path}")
    if path.suffix.lower() in {".csv", ".txt"}:
        raw = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        raw = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported instrument file type: {path.suffix}")

    missing = [col for col in [spec.date_column, spec.value_column] if col not in raw.columns]
    if missing:
        raise KeyError(f"Instrument file is missing required columns: {missing}")

    series = pd.Series(
        pd.to_numeric(raw[spec.value_column], errors="coerce").to_numpy(),
        index=pd.to_datetime(raw[spec.date_column]),
        name=spec.name,
    ).dropna()
    if spec.frequency == "quarterly":
        series.index = series.index.to_period("Q").to_timestamp("Q")
        series = series.groupby(level=0).sum()
    return series.sort_index()


def align_instrument_to_residuals(residuals: pd.DataFrame, instrument: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    joined_index = residuals.index.intersection(instrument.index)
    aligned_residuals = residuals.loc[joined_index].dropna()
    aligned_instrument = instrument.loc[aligned_residuals.index].dropna()
    aligned_residuals = aligned_residuals.loc[aligned_instrument.index]
    if aligned_residuals.empty:
        raise ValueError("No overlapping observations between SVECM residuals and external instrument.")
    return aligned_residuals, aligned_instrument


def first_stage_relevance(
    residuals: pd.DataFrame,
    instrument: pd.Series,
    policy_residual_column: str,
) -> pd.DataFrame:
    aligned_residuals, aligned_instrument = align_instrument_to_residuals(residuals, instrument)
    if policy_residual_column not in aligned_residuals.columns:
        raise KeyError(f"Policy residual column not found: {policy_residual_column}")
    x = sm.add_constant(aligned_instrument)
    y = aligned_residuals[policy_residual_column]
    model = sm.OLS(y, x).fit()
    return pd.DataFrame(
        [
            {
                "instrument": instrument.name,
                "policy_residual": policy_residual_column,
                "nobs": int(model.nobs),
                "coefficient": float(model.params.iloc[1]),
                "std_error": float(model.bse.iloc[1]),
                "t_stat": float(model.tvalues.iloc[1]),
                "f_stat": float(model.fvalue),
                "p_value": float(model.pvalues.iloc[1]),
                "r_squared": float(model.rsquared),
            }
        ]
    )


def proxy_impact_vector(
    residuals: pd.DataFrame,
    instrument: pd.Series,
    policy_residual_column: str,
    expansionary_policy_impact: float = -1.0,
) -> pd.Series:
    """Recover a normalized proxy impact vector from reduced-form residuals.

    This is infrastructure only. The final thesis run must provide validated
    SVECM residuals and an ECB monetary-surprise instrument before using it.
    """

    aligned_residuals, aligned_instrument = align_instrument_to_residuals(residuals, instrument)
    z = aligned_instrument.to_numpy()
    u = aligned_residuals.to_numpy()
    raw = (z.reshape(1, -1) @ u).flatten() / len(aligned_residuals)
    impact = pd.Series(raw, index=aligned_residuals.columns, name="proxy_impact")
    if np.isclose(impact[policy_residual_column], 0.0):
        raise ValueError("Cannot normalize proxy impact: zero covariance with policy residual.")
    impact = impact / abs(impact[policy_residual_column])
    if np.sign(impact[policy_residual_column]) != np.sign(expansionary_policy_impact):
        impact = -impact
    return impact * (abs(expansionary_policy_impact) / abs(impact[policy_residual_column]))
