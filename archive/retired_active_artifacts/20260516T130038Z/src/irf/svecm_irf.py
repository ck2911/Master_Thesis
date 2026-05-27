from __future__ import annotations

import numpy as np
import pandas as pd


def structural_irf_table(vecm_result, impact: pd.Series, periods: int = 20) -> pd.DataFrame:
    """Map a proxy impact vector through a fitted VECM's moving-average response.

    This helper is SVECM-ready but does not fit or identify the final model.
    """

    irf = vecm_result.irf(periods)
    variables = list(impact.index)
    b = impact.loc[variables].to_numpy()
    responses = np.array([irf.irfs[h] @ b for h in range(irf.irfs.shape[0])])
    rows = []
    for horizon in range(responses.shape[0]):
        for idx, response in enumerate(variables):
            rows.append({"horizon": horizon, "response": response, "irf": responses[horizon, idx]})
    return pd.DataFrame(rows)
