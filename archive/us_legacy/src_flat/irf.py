from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .diagnostics import residual_frame


def standard_irf_table(result, variables: list[str], periods: int = 36) -> pd.DataFrame:
    irf = result.irf(periods)
    rows = []
    for horizon in range(irf.irfs.shape[0]):
        for impulse_idx, impulse in enumerate(variables):
            for response_idx, response in enumerate(variables):
                rows.append(
                    {
                        "horizon": horizon,
                        "impulse": impulse,
                        "response": response,
                        "irf": irf.irfs[horizon, response_idx, impulse_idx],
                    }
                )
    return pd.DataFrame(rows)


def proxy_first_stage(
    result,
    data_index: pd.DatetimeIndex,
    variables: list[str],
    shocks: pd.DataFrame,
    policy_column: str,
    shock_column: str,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, object]:
    resid = residual_frame(result, data_index, variables)
    joined_index = resid.index.intersection(shocks.index)
    resid = resid.loc[joined_index]
    instrument = shocks.loc[joined_index, shock_column].dropna()
    joined_index = resid.index.intersection(instrument.index)
    resid = resid.loc[joined_index]
    instrument = instrument.loc[joined_index]

    y = resid[policy_column]
    x = sm.add_constant(instrument)
    first_stage = sm.OLS(y, x).fit()
    return instrument, resid, y, first_stage


def proxy_impact_vector(
    residuals: pd.DataFrame,
    instrument: pd.Series,
    policy_column: str,
    expansionary_policy_impact: float = -1.0,
) -> pd.Series:
    aligned = residuals.join(instrument.rename("instrument"), how="inner")
    z = aligned["instrument"].to_numpy()
    u = aligned[residuals.columns].to_numpy()
    raw = (z.reshape(1, -1) @ u).flatten() / len(aligned)
    raw = pd.Series(raw, index=residuals.columns, name="raw_covariance")

    if np.isclose(raw[policy_column], 0.0):
        raise ValueError("Cannot normalize proxy shock: zero covariance with policy residual.")

    normalized = raw / abs(raw[policy_column])
    if np.sign(normalized[policy_column]) != np.sign(expansionary_policy_impact):
        normalized = -normalized
    normalized = normalized * (abs(expansionary_policy_impact) / abs(normalized[policy_column]))
    normalized.name = "impact"
    return normalized


def proxy_irf_table(result, impact: pd.Series, periods: int = 36) -> pd.DataFrame:
    irf = result.irf(periods)
    b = impact.loc[list(impact.index)].to_numpy()
    responses = np.array([irf.irfs[h] @ b for h in range(irf.irfs.shape[0])])
    rows = []
    for horizon in range(responses.shape[0]):
        for idx, variable in enumerate(impact.index):
            rows.append(
                {
                    "horizon": horizon,
                    "response": variable,
                    "irf": responses[horizon, idx],
                }
            )
    return pd.DataFrame(rows)


def first_stage_table(first_stage) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "nobs": int(first_stage.nobs),
                "coef": float(first_stage.params.iloc[1]),
                "std_error": float(first_stage.bse.iloc[1]),
                "t_stat": float(first_stage.tvalues.iloc[1]),
                "f_stat": float(first_stage.fvalue),
                "p_value": float(first_stage.pvalues.iloc[1]),
                "r_squared": float(first_stage.rsquared),
            }
        ]
    )

