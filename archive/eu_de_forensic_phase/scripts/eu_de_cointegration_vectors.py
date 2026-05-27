#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_coint_rank


ROOT = Path.cwd()
TABLE_DIR = ROOT / "results" / "eu_de_forensic" / "tables"
q = pd.read_csv(TABLE_DIR / "eu_de_quarterly_clean.csv", parse_dates=["date"]).set_index("date").sort_index()

for col in q.columns:
    if (q[col].dropna() > 0).all():
        q[f"ln_{col}"] = np.log(q[col])

SYSTEMS = {
    "core_real_credit_house_income": [
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
    ],
    "core_plus_real_dax": [
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
        "ln_dax_real_de",
    ],
    "nominal_credit_house_income_prices": [
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de",
        "ln_compensation_ea20_nominal",
        "ln_hicp_de",
    ],
}

SAMPLES = {
    "full": (None, None),
    "pre_covid": (None, "2019-12-31"),
    "post_2014_to_pre_tightening": ("2014-03-31", "2022-06-30"),
}

rows = []
for system, cols in SYSTEMS.items():
    base = q[cols].dropna()
    for sample_name, (start, end) in SAMPLES.items():
        data = base.copy()
        if start is not None:
            data = data.loc[start:]
        if end is not None:
            data = data.loc[:end]
        if len(data) < max(36, len(cols) * 8):
            rows.append(
                {
                    "system": system,
                    "sample": sample_name,
                    "nobs": len(data),
                    "error": "too few observations for stable vector inspection",
                }
            )
            continue
        for det_order in [0]:
            for lag in [1, 2]:
                try:
                    joh = coint_johansen(data, det_order=det_order, k_ar_diff=lag)
                    trace_rank = select_coint_rank(
                        data, det_order=det_order, k_ar_diff=lag, method="trace", signif=0.05
                    ).rank
                    beta = joh.evec[:, 0]
                    if abs(beta[0]) > 1e-12:
                        beta = beta / beta[0]
                    row = {
                        "system": system,
                        "sample": sample_name,
                        "nobs": len(data),
                        "sample_start": data.index.min().date(),
                        "sample_end": data.index.max().date(),
                        "det_order": det_order,
                        "k_ar_diff": lag,
                        "trace_rank_5pct": int(trace_rank),
                        "normalization": cols[0],
                        "error": "",
                    }
                    row.update({f"beta_{col}": beta[i] for i, col in enumerate(cols)})
                    rows.append(row)
                except Exception as exc:
                    rows.append(
                        {
                            "system": system,
                            "sample": sample_name,
                            "nobs": len(data),
                            "det_order": det_order,
                            "k_ar_diff": lag,
                            "error": str(exc),
                        }
                    )

out = pd.DataFrame(rows)
out.to_csv(TABLE_DIR / "cointegrating_vector_stability.csv", index=False)
print(out.to_string(index=False))
