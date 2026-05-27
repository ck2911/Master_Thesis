from __future__ import annotations

import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_coint_rank, select_order


DET_ORDER_LABELS = {
    -1: "none",
    0: "constant_in_cointegration_relation",
    1: "linear_trend",
}


def lag_selection_table(data: pd.DataFrame, maxlags: int = 12, deterministic: str = "co") -> tuple[pd.DataFrame, dict[str, int]]:
    result = select_order(data, maxlags=maxlags, deterministic=deterministic)
    rows = []
    for lag in range(maxlags + 1):
        rows.append(
            {
                "k_ar_diff": lag,
                "aic": result.ics["aic"][lag],
                "bic": result.ics["bic"][lag],
                "hqic": result.ics["hqic"][lag],
                "fpe": result.ics["fpe"][lag],
            }
        )
    return pd.DataFrame(rows), dict(result.selected_orders)


def johansen_rank_table(
    data: pd.DataFrame,
    k_ar_diff: int,
    det_order: int = 0,
    alpha_index: int = 1,
) -> pd.DataFrame:
    """Return Johansen trace and max-eigen statistics.

    alpha_index selects the critical-value column from statsmodels:
    0=90%, 1=95%, 2=99%.
    """

    joh = coint_johansen(data, det_order=det_order, k_ar_diff=k_ar_diff)
    rows = []
    k = data.shape[1]
    for rank in range(k):
        rows.append(
            {
                "r_null": rank,
                "r_alt_trace": k,
                "trace_stat": float(joh.lr1[rank]),
                "trace_crit_95": float(joh.cvt[rank, alpha_index]),
                "trace_reject_95": bool(joh.lr1[rank] > joh.cvt[rank, alpha_index]),
                "r_alt_maxeig": rank + 1,
                "maxeig_stat": float(joh.lr2[rank]),
                "maxeig_crit_95": float(joh.cvm[rank, alpha_index]),
                "maxeig_reject_95": bool(joh.lr2[rank] > joh.cvm[rank, alpha_index]),
                "det_order": det_order,
                "deterministic_label": DET_ORDER_LABELS.get(det_order, str(det_order)),
                "k_ar_diff": k_ar_diff,
            }
        )
    return pd.DataFrame(rows)


def selected_rank(data: pd.DataFrame, k_ar_diff: int, det_order: int = 0, method: str = "trace") -> int:
    result = select_coint_rank(
        data,
        det_order=det_order,
        k_ar_diff=k_ar_diff,
        method=method,
        signif=0.05,
    )
    return int(result.rank)


def rank_sensitivity_table(data: pd.DataFrame, lag_values: list[int], det_orders: list[int]) -> pd.DataFrame:
    rows = []
    for lag in lag_values:
        for det_order in det_orders:
            try:
                rows.append(
                    {
                        "k_ar_diff": lag,
                        "det_order": det_order,
                        "deterministic_label": DET_ORDER_LABELS.get(det_order, str(det_order)),
                        "trace_rank_5pct": selected_rank(data, lag, det_order, method="trace"),
                        "maxeig_rank_5pct": selected_rank(data, lag, det_order, method="maxeig"),
                        "error": "",
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "k_ar_diff": lag,
                        "det_order": det_order,
                        "deterministic_label": DET_ORDER_LABELS.get(det_order, str(det_order)),
                        "trace_rank_5pct": pd.NA,
                        "maxeig_rank_5pct": pd.NA,
                        "error": str(exc),
                    }
                )
    return pd.DataFrame(rows)


def cointegration_gate(rank: int, n_variables: int) -> tuple[bool, str]:
    if rank <= 0:
        return False, "Cointegration gate failed. Johansen testing selected rank 0."
    if rank >= n_variables:
        return False, "Cointegration gate failed. Selected rank implies full rank/stationary system."
    return True, f"Cointegration gate passed with rank {rank} of {n_variables}."

