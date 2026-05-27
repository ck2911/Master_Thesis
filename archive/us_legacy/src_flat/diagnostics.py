from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.stats.stattools import jarque_bera


def residual_frame(result, index: pd.DatetimeIndex, columns: list[str]) -> pd.DataFrame:
    resid = pd.DataFrame(result.resid, columns=columns)
    resid.index = index[-len(resid) :]
    return resid


def residual_diagnostics(result, index: pd.DatetimeIndex, columns: list[str], lags: int = 12) -> pd.DataFrame:
    resid = residual_frame(result, index, columns)
    rows = []
    for col in resid.columns:
        series = resid[col].dropna()
        lb = acorr_ljungbox(series, lags=[lags], return_df=True)
        arch_stat, arch_p, _, _ = het_arch(series, nlags=min(lags, max(1, len(series) // 5)))
        jb_stat, jb_p, skew, kurtosis = jarque_bera(series)
        rows.append(
            {
                "equation": col,
                "ljung_box_lag": lags,
                "ljung_box_pvalue": float(lb["lb_pvalue"].iloc[0]),
                "arch_lm_pvalue": float(arch_p),
                "jarque_bera_pvalue": float(jb_p),
                "skew": float(skew),
                "kurtosis": float(kurtosis),
            }
        )
    return pd.DataFrame(rows)


def model_level_tests(result) -> pd.DataFrame:
    rows = []
    for name, method in [("whiteness", "test_whiteness"), ("normality", "test_normality")]:
        if hasattr(result, method):
            try:
                test = getattr(result, method)()
                rows.append(
                    {
                        "test": name,
                        "statistic": getattr(test, "test_statistic", np.nan),
                        "p_value": getattr(test, "pvalue", np.nan),
                        "summary": str(test.summary()),
                        "error": "",
                    }
                )
            except Exception as exc:
                rows.append({"test": name, "statistic": np.nan, "p_value": np.nan, "summary": "", "error": str(exc)})
    return pd.DataFrame(rows)


def companion_eigenvalues(result) -> pd.DataFrame:
    var_rep = np.asarray(result.var_rep)
    if var_rep.ndim != 3:
        return pd.DataFrame()
    p, k, _ = var_rep.shape
    top = np.concatenate(var_rep, axis=1)
    if p == 1:
        companion = top
    else:
        identity = np.eye(k * (p - 1))
        zeros = np.zeros((k * (p - 1), k))
        companion = np.vstack([top, np.hstack([identity, zeros])])
    eigvals = np.linalg.eigvals(companion)
    return pd.DataFrame(
        {
            "real": eigvals.real,
            "imag": eigvals.imag,
            "modulus": np.abs(eigvals),
        }
    ).sort_values("modulus", ascending=False)


def covid_break_screen(data: pd.DataFrame, split_date: str) -> pd.DataFrame:
    diff = data.diff().dropna()
    pre = diff.loc[:split_date]
    post = diff.loc[split_date:]
    rows = []
    for col in data.columns:
        pre_series = pre[col].dropna()
        post_series = post[col].dropna()
        if len(pre_series) < 5 or len(post_series) < 5:
            rows.append(
                {
                    "variable": col,
                    "pre_mean": np.nan,
                    "post_mean": np.nan,
                    "welch_t_pvalue": np.nan,
                    "pre_std": np.nan,
                    "post_std": np.nan,
                    "variance_ratio_post_pre": np.nan,
                }
            )
            continue
        ttest = stats.ttest_ind(pre_series, post_series, equal_var=False, nan_policy="omit")
        pre_std = pre_series.std()
        post_std = post_series.std()
        rows.append(
            {
                "variable": col,
                "pre_mean": float(pre_series.mean()),
                "post_mean": float(post_series.mean()),
                "welch_t_pvalue": float(ttest.pvalue),
                "pre_std": float(pre_std),
                "post_std": float(post_std),
                "variance_ratio_post_pre": float((post_std**2) / (pre_std**2)) if pre_std else np.nan,
            }
        )
    return pd.DataFrame(rows)


def diagnostics_gate(residual_table: pd.DataFrame, alpha: float = 0.05) -> tuple[bool, str]:
    autocorr_fail = residual_table.loc[residual_table["ljung_box_pvalue"] < alpha, "equation"].tolist()
    hetero_fail = residual_table.loc[residual_table["arch_lm_pvalue"] < alpha, "equation"].tolist()
    issues = []
    if autocorr_fail:
        issues.append(f"autocorrelation in {autocorr_fail}")
    if hetero_fail:
        issues.append(f"ARCH effects in {hetero_fail}")
    if issues:
        return False, "Diagnostics gate warning: " + "; ".join(issues)
    return True, "Residual diagnostics gate passed for autocorrelation and ARCH screens."

