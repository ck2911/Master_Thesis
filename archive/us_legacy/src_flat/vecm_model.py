from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.vector_ar.vecm import VECM


def fit_vecm(data: pd.DataFrame, k_ar_diff: int, coint_rank: int, deterministic: str = "co"):
    model = VECM(
        data,
        k_ar_diff=k_ar_diff,
        coint_rank=coint_rank,
        deterministic=deterministic,
    )
    return model.fit()


def _pvalues_from_tvalues(tvalues: np.ndarray) -> np.ndarray:
    return 2.0 * stats.norm.sf(np.abs(tvalues))


def alpha_table(result, variables: list[str]) -> pd.DataFrame:
    alpha = np.asarray(result.alpha)
    stderr = np.asarray(getattr(result, "stderr_alpha", np.full_like(alpha, np.nan)))
    tvalues = np.divide(alpha, stderr, out=np.full_like(alpha, np.nan), where=stderr != 0)
    pvalues = _pvalues_from_tvalues(tvalues)
    rows = []
    for i, variable in enumerate(variables):
        for j in range(alpha.shape[1]):
            rows.append(
                {
                    "equation": variable,
                    "cointegration_relation": f"ec{j + 1}",
                    "alpha": alpha[i, j],
                    "std_error": stderr[i, j],
                    "z_value": tvalues[i, j],
                    "p_value": pvalues[i, j],
                }
            )
    return pd.DataFrame(rows)


def beta_table(result, variables: list[str]) -> pd.DataFrame:
    beta = np.asarray(result.beta)
    rows = []
    for i, variable in enumerate(variables):
        for j in range(beta.shape[1]):
            rows.append(
                {
                    "variable": variable,
                    "cointegration_relation": f"ec{j + 1}",
                    "beta": beta[i, j],
                }
            )
    return pd.DataFrame(rows)


def short_run_table(result, variables: list[str]) -> pd.DataFrame:
    gamma = np.asarray(result.gamma)
    if gamma.size == 0:
        return pd.DataFrame()
    k = len(variables)
    rows = []
    for equation_idx, equation in enumerate(variables):
        for col_idx in range(gamma.shape[1]):
            lag = col_idx // k + 1
            variable = variables[col_idx % k]
            rows.append(
                {
                    "equation": equation,
                    "lag": lag,
                    "d_variable": f"D.{variable}",
                    "coefficient": gamma[equation_idx, col_idx],
                }
            )
    return pd.DataFrame(rows)


def significance_gate(alpha: pd.DataFrame, min_significant_adjustments: int = 1) -> tuple[bool, str]:
    significant = alpha.loc[alpha["p_value"] < 0.05]
    if len(significant) >= min_significant_adjustments:
        return True, f"Adjustment gate passed. {len(significant)} alpha coefficients are significant at 5%."
    return False, "Adjustment gate failed. No economically useful error-correction adjustment is significant."

