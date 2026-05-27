from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

try:
    from arch.unitroot import PhillipsPerron
except Exception:  # pragma: no cover - optional dependency
    PhillipsPerron = None


def _safe_adf(series: pd.Series, regression: str) -> dict[str, float | str]:
    try:
        stat, pvalue, usedlag, nobs, *_ = adfuller(
            series.dropna(), regression=regression, autolag="AIC"
        )
        return {
            "stat": float(stat),
            "pvalue": float(pvalue),
            "used_lag": int(usedlag),
            "nobs": int(nobs),
            "error": "",
        }
    except Exception as exc:
        return {"stat": np.nan, "pvalue": np.nan, "used_lag": np.nan, "nobs": np.nan, "error": str(exc)}


def _safe_kpss(series: pd.Series, regression: str) -> dict[str, float | str]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stat, pvalue, usedlag, _ = kpss(series.dropna(), regression=regression, nlags="auto")
        return {
            "stat": float(stat),
            "pvalue": float(pvalue),
            "used_lag": int(usedlag),
            "error": "",
        }
    except Exception as exc:
        return {"stat": np.nan, "pvalue": np.nan, "used_lag": np.nan, "error": str(exc)}


def _safe_pp(series: pd.Series, trend: str) -> dict[str, float | str]:
    if PhillipsPerron is None:
        return {
            "stat": np.nan,
            "pvalue": np.nan,
            "used_lag": np.nan,
            "error": "Optional dependency arch is not installed.",
        }
    try:
        test = PhillipsPerron(series.dropna(), trend=trend)
        return {
            "stat": float(test.stat),
            "pvalue": float(test.pvalue),
            "used_lag": int(test.lags),
            "error": "",
        }
    except Exception as exc:
        return {"stat": np.nan, "pvalue": np.nan, "used_lag": np.nan, "error": str(exc)}


def classify_integration(row: pd.Series, alpha: float = 0.05) -> str:
    adf_level = row["adf_c_level_pvalue"]
    kpss_level = row["kpss_c_level_pvalue"]
    adf_diff = row["adf_c_diff_pvalue"]
    kpss_diff = row["kpss_c_diff_pvalue"]
    adf_trend = row["adf_ct_level_pvalue"]
    kpss_trend = row["kpss_ct_level_pvalue"]

    if pd.notna(adf_level) and pd.notna(kpss_level):
        if adf_level < alpha and kpss_level > alpha:
            return "I(0)"

    if all(pd.notna(x) for x in [adf_level, kpss_level, adf_diff, kpss_diff]):
        if adf_level > alpha and kpss_level < alpha and adf_diff < alpha and kpss_diff > alpha:
            return "I(1)"

    if pd.notna(adf_trend) and pd.notna(kpss_trend):
        if adf_trend < alpha and kpss_trend > alpha:
            return "trend-stationary"

    if pd.notna(adf_diff) and pd.notna(kpss_diff):
        if adf_diff < alpha and kpss_diff > alpha:
            return "difference-stationary/ambiguous"

    return "unclear"


def stationarity_table(data: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    rows = []
    for variable in data.columns:
        level = data[variable].dropna()
        diff = level.diff().dropna()

        adf_c_level = _safe_adf(level, regression="c")
        adf_ct_level = _safe_adf(level, regression="ct")
        adf_c_diff = _safe_adf(diff, regression="c")
        kpss_c_level = _safe_kpss(level, regression="c")
        kpss_ct_level = _safe_kpss(level, regression="ct")
        kpss_c_diff = _safe_kpss(diff, regression="c")
        pp_c_level = _safe_pp(level, trend="c")
        pp_c_diff = _safe_pp(diff, trend="c")

        row = {
            "variable": variable,
            "nobs": int(level.shape[0]),
            "adf_c_level_stat": adf_c_level["stat"],
            "adf_c_level_pvalue": adf_c_level["pvalue"],
            "adf_ct_level_stat": adf_ct_level["stat"],
            "adf_ct_level_pvalue": adf_ct_level["pvalue"],
            "kpss_c_level_stat": kpss_c_level["stat"],
            "kpss_c_level_pvalue": kpss_c_level["pvalue"],
            "kpss_ct_level_stat": kpss_ct_level["stat"],
            "kpss_ct_level_pvalue": kpss_ct_level["pvalue"],
            "adf_c_diff_stat": adf_c_diff["stat"],
            "adf_c_diff_pvalue": adf_c_diff["pvalue"],
            "pp_c_level_stat": pp_c_level["stat"],
            "pp_c_level_pvalue": pp_c_level["pvalue"],
            "pp_c_diff_stat": pp_c_diff["stat"],
            "pp_c_diff_pvalue": pp_c_diff["pvalue"],
            "pp_note": pp_c_level["error"] or pp_c_diff["error"],
            "kpss_c_diff_stat": kpss_c_diff["stat"],
            "kpss_c_diff_pvalue": kpss_c_diff["pvalue"],
        }
        row["integration_order"] = classify_integration(pd.Series(row), alpha=alpha)
        rows.append(row)

    return pd.DataFrame(rows)


def stationarity_gate(table: pd.DataFrame, required: str = "I(1)") -> tuple[bool, str]:
    bad = table.loc[table["integration_order"] != required, ["variable", "integration_order"]]
    if bad.empty:
        return True, f"All variables are classified as {required}."

    details = "; ".join(f"{r.variable}={r.integration_order}" for r in bad.itertuples())
    return False, f"Stationarity gate failed. Non-{required} classifications: {details}."
