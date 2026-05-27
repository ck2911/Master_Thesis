from __future__ import annotations

import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_coint_rank, select_order


DET_ORDER_LABELS = {
    -1: "none",
    0: "constant",
    1: "linear_trend",
}


def lag_selection_table(data: pd.DataFrame, maxlags: int = 4, deterministic: str = "ci") -> pd.DataFrame:
    result = select_order(data.dropna(), maxlags=maxlags, deterministic=deterministic)
    rows = []
    for lag in range(maxlags + 1):
        rows.append(
            {
                "k_ar_diff": lag,
                "aic": result.ics["aic"][lag],
                "bic": result.ics["bic"][lag],
                "hqic": result.ics["hqic"][lag],
                "fpe": result.ics["fpe"][lag],
                "selected_aic": result.selected_orders["aic"],
                "selected_bic": result.selected_orders["bic"],
                "selected_hqic": result.selected_orders["hqic"],
            }
        )
    return pd.DataFrame(rows)


def rank_sensitivity_table(
    data: pd.DataFrame,
    lag_values: list[int],
    det_orders: list[int],
    system_name: str,
) -> pd.DataFrame:
    clean = data.dropna()
    rows = []
    for det_order in det_orders:
        for lag in lag_values:
            try:
                joh = coint_johansen(clean, det_order=det_order, k_ar_diff=lag)
                trace_rank = select_coint_rank(clean, det_order=det_order, k_ar_diff=lag, method="trace", signif=0.05).rank
                maxeig_rank = select_coint_rank(clean, det_order=det_order, k_ar_diff=lag, method="maxeig", signif=0.05).rank
                for rank in range(clean.shape[1]):
                    rows.append(
                        {
                            "system": system_name,
                            "nobs": clean.shape[0],
                            "sample_start": clean.index.min(),
                            "sample_end": clean.index.max(),
                            "variables": ",".join(clean.columns),
                            "det_order": det_order,
                            "deterministic": DET_ORDER_LABELS.get(det_order, str(det_order)),
                            "k_ar_diff": lag,
                            "r_null": rank,
                            "trace_stat": float(joh.lr1[rank]),
                            "trace_crit_95": float(joh.cvt[rank, 1]),
                            "trace_reject_95": bool(joh.lr1[rank] > joh.cvt[rank, 1]),
                            "maxeig_stat": float(joh.lr2[rank]),
                            "maxeig_crit_95": float(joh.cvm[rank, 1]),
                            "maxeig_reject_95": bool(joh.lr2[rank] > joh.cvm[rank, 1]),
                            "selected_trace_rank_5pct": int(trace_rank),
                            "selected_maxeig_rank_5pct": int(maxeig_rank),
                            "error": "",
                        }
                    )
            except Exception as exc:
                rows.append(
                    {
                        "system": system_name,
                        "nobs": clean.shape[0],
                        "variables": ",".join(clean.columns),
                        "det_order": det_order,
                        "deterministic": DET_ORDER_LABELS.get(det_order, str(det_order)),
                        "k_ar_diff": lag,
                        "error": str(exc),
                    }
                )
    return pd.DataFrame(rows)
