#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from arch.unitroot import PhillipsPerron
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.vector_ar.vecm import coint_johansen, select_coint_rank, select_order


ROOT = Path.cwd()
TABLE_DIR = ROOT / "results" / "eu_de_forensic" / "tables"
FIG_DIR = ROOT / "results" / "eu_de_forensic" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


QUARTERLY_PATH = TABLE_DIR / "eu_de_quarterly_clean.csv"
MONTHLY_PATH = TABLE_DIR / "eu_de_monthly_clean.csv"
ANNUAL_PATH = TABLE_DIR / "eurosystem_balance_sheet_annual_clean.csv"


def load_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.set_index("date").sort_index()


q = load_frame(QUARTERLY_PATH)
m = load_frame(MONTHLY_PATH)
annual = load_frame(ANNUAL_PATH)


LEVEL_TEST_VARIABLES = [
    "wx_shadow_rate",
    "dfr_eop",
    "hh_loans_ea_stock",
    "nfc_loans_ea_stock",
    "credit_standards_enterprise",
    "credit_standards_household",
    "house_price_de",
    "house_price_de_real",
    "compensation_ea20_nominal",
    "compensation_ea20_real",
    "dax_close",
    "dax_real_de",
    "retail_de_mom_pct",
    "retail_de_chained_index",
    "hicp_de",
    "hicp_ea20",
    "ecb_total_assets",
    "ecb_monetary_policy_securities",
]

RATE_OR_STATIONARY = {
    "wx_shadow_rate",
    "dfr_eop",
    "dfr_avg",
    "credit_standards_enterprise",
    "credit_standards_household",
    "retail_de_mom_pct",
}


def safe_adf(s: pd.Series, regression: str = "c") -> dict:
    s = s.dropna()
    if len(s) < 12 or s.nunique() < 3:
        return {"stat": np.nan, "pvalue": np.nan, "lags": np.nan, "nobs": len(s), "error": "too few observations or near-constant"}
    try:
        stat, pvalue, usedlag, nobs, *_ = adfuller(s, regression=regression, autolag="AIC")
        return {"stat": stat, "pvalue": pvalue, "lags": usedlag, "nobs": nobs, "error": ""}
    except Exception as exc:
        return {"stat": np.nan, "pvalue": np.nan, "lags": np.nan, "nobs": len(s), "error": str(exc)}


def safe_kpss(s: pd.Series, regression: str = "c") -> dict:
    s = s.dropna()
    if len(s) < 12 or s.nunique() < 3:
        return {"stat": np.nan, "pvalue": np.nan, "lags": np.nan, "error": "too few observations or near-constant"}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stat, pvalue, usedlag, _ = kpss(s, regression=regression, nlags="auto")
        return {"stat": stat, "pvalue": pvalue, "lags": usedlag, "error": ""}
    except Exception as exc:
        return {"stat": np.nan, "pvalue": np.nan, "lags": np.nan, "error": str(exc)}


def safe_pp(s: pd.Series, trend: str = "c") -> dict:
    s = s.dropna()
    if len(s) < 12 or s.nunique() < 3:
        return {"stat": np.nan, "pvalue": np.nan, "lags": np.nan, "error": "too few observations or near-constant"}
    try:
        test = PhillipsPerron(s, trend=trend)
        return {"stat": test.stat, "pvalue": test.pvalue, "lags": test.lags, "error": ""}
    except Exception as exc:
        return {"stat": np.nan, "pvalue": np.nan, "lags": np.nan, "error": str(exc)}


def classify(row: pd.Series, alpha: float = 0.05) -> str:
    adf_l = row.get("adf_c_level_p")
    kpss_l = row.get("kpss_c_level_p")
    adf_d = row.get("adf_c_diff_p")
    kpss_d = row.get("kpss_c_diff_p")
    adf_t = row.get("adf_ct_level_p")
    kpss_t = row.get("kpss_ct_level_p")
    if pd.notna(adf_l) and pd.notna(kpss_l) and adf_l < alpha and kpss_l > alpha:
        return "I(0)"
    if all(pd.notna(x) for x in [adf_l, kpss_l, adf_d, kpss_d]):
        if adf_l > alpha and kpss_l < alpha and adf_d < alpha and kpss_d > alpha:
            return "I(1)"
    if pd.notna(adf_t) and pd.notna(kpss_t) and adf_t < alpha and kpss_t > alpha:
        return "trend-stationary"
    if pd.notna(adf_d) and pd.notna(kpss_d) and adf_d < alpha and kpss_d > alpha:
        return "difference-stationary/ambiguous"
    if pd.notna(adf_d) and adf_d < alpha:
        return "near-I(1)/ambiguous"
    return "unclear"


def preferred_level(df: pd.DataFrame, var: str) -> tuple[pd.Series, str]:
    s = df[var].dropna()
    if var not in RATE_OR_STATIONARY and (s > 0).all():
        return np.log(s), "log"
    return s, "level"


def stationarity_table(df: pd.DataFrame, variables: list[str], dataset: str, yoy_lag: int) -> pd.DataFrame:
    rows = []
    for var in variables:
        if var not in df.columns:
            continue
        raw = df[var].dropna()
        if raw.empty:
            continue
        pref, pref_transform = preferred_level(df, var)
        candidates = {
            "preferred_level": pref,
            "level": raw,
            "first_diff_preferred": pref.diff(),
            "yoy_diff_preferred": pref.diff(yoy_lag),
        }
        if (raw > 0).all():
            candidates["log_level"] = np.log(raw)
            candidates["log_diff"] = np.log(raw).diff()
            candidates["yoy_log_diff"] = np.log(raw).diff(yoy_lag)
        for transform, series in candidates.items():
            series = series.dropna()
            adf_c = safe_adf(series, "c")
            adf_ct = safe_adf(series, "ct")
            kpss_c = safe_kpss(series, "c")
            kpss_ct = safe_kpss(series, "ct")
            pp_c = safe_pp(series, "c")
            diff = series.diff().dropna()
            adf_d = safe_adf(diff, "c")
            kpss_d = safe_kpss(diff, "c")
            row = {
                "dataset": dataset,
                "variable": var,
                "transform": transform,
                "preferred_level_transform": pref_transform,
                "nobs": int(series.shape[0]),
                "start": series.index.min().date() if len(series) else None,
                "end": series.index.max().date() if len(series) else None,
                "adf_c_level_stat": adf_c["stat"],
                "adf_c_level_p": adf_c["pvalue"],
                "adf_ct_level_stat": adf_ct["stat"],
                "adf_ct_level_p": adf_ct["pvalue"],
                "kpss_c_level_stat": kpss_c["stat"],
                "kpss_c_level_p": kpss_c["pvalue"],
                "kpss_ct_level_stat": kpss_ct["stat"],
                "kpss_ct_level_p": kpss_ct["pvalue"],
                "pp_c_level_stat": pp_c["stat"],
                "pp_c_level_p": pp_c["pvalue"],
                "adf_c_diff_p": adf_d["pvalue"],
                "kpss_c_diff_p": kpss_d["pvalue"],
                "test_notes": "; ".join(
                    sorted(
                        {
                            note
                            for note in [
                                adf_c["error"],
                                adf_ct["error"],
                                kpss_c["error"],
                                kpss_ct["error"],
                                pp_c["error"],
                            ]
                            if note
                        }
                    )
                ),
            }
            row["classification"] = classify(pd.Series(row))
            rows.append(row)
    return pd.DataFrame(rows)


stationarity_q = stationarity_table(q, LEVEL_TEST_VARIABLES, "quarterly", 4)
stationarity_m = stationarity_table(
    m,
    [
        "wx_shadow_rate",
        "dfr_eop",
        "hh_loans_ea_stock",
        "nfc_loans_ea_stock",
        "dax_close",
        "dax_real_de",
        "retail_de_mom_pct",
        "retail_de_chained_index",
        "hicp_de",
        "hicp_ea20",
    ],
    "monthly",
    12,
)
stationarity_q.to_csv(TABLE_DIR / "stationarity_quarterly_all_transforms.csv", index=False)
stationarity_m.to_csv(TABLE_DIR / "stationarity_monthly_all_transforms.csv", index=False)

preferred_rows = stationarity_q[stationarity_q["transform"] == "preferred_level"].copy()
preferred_rows.to_csv(TABLE_DIR / "stationarity_quarterly_preferred_levels.csv", index=False)


def plot_diagnostics(df: pd.DataFrame, var: str, freq_label: str) -> None:
    if var not in df.columns:
        return
    s = df[var].dropna()
    if len(s) < 8:
        return
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    axes = axes.ravel()
    s.plot(ax=axes[0], title=f"{var}: level")
    if (s > 0).all():
        logs = np.log(s)
        logs.plot(ax=axes[1], title="log level")
        (100 * logs.diff()).plot(ax=axes[2], title="growth, log difference (%)")
        lag = 4 if freq_label == "quarterly" else 12
        (100 * logs.diff(lag)).plot(ax=axes[3], title="YoY log growth (%)")
    else:
        axes[1].axis("off")
        s.diff().plot(ax=axes[2], title="first difference")
        lag = 4 if freq_label == "quarterly" else 12
        s.diff(lag).plot(ax=axes[3], title="YoY/4-quarter difference")
    for ax in axes:
        ax.grid(True, alpha=0.25)
    fig.suptitle(f"{freq_label.capitalize()} diagnostics: {var}", fontsize=14)
    fig.savefig(FIG_DIR / f"{freq_label}_{var}_diagnostics.png", dpi=160)
    plt.close(fig)


for variable in LEVEL_TEST_VARIABLES:
    plot_diagnostics(q, variable, "quarterly")


def chow_break(series: pd.Series, break_date: str) -> dict:
    y = series.dropna()
    if len(y) < 24:
        return {"break_date": break_date, "f_stat": np.nan, "pvalue": np.nan, "nobs": len(y), "note": "too few observations"}
    bdate = pd.Timestamp(break_date)
    if bdate not in y.index:
        candidates = y.index[y.index <= bdate]
        if len(candidates) == 0:
            return {"break_date": break_date, "f_stat": np.nan, "pvalue": np.nan, "nobs": len(y), "note": "break before sample"}
        bdate = candidates.max()
    loc = y.index.get_loc(bdate)
    if isinstance(loc, slice):
        loc = loc.start
    if loc < 8 or len(y) - loc - 1 < 8:
        return {"break_date": str(bdate.date()), "f_stat": np.nan, "pvalue": np.nan, "nobs": len(y), "note": "insufficient pre/post observations"}
    t = np.arange(len(y))
    x_full = add_constant(t)
    full = OLS(y.values, x_full).fit()
    pre = OLS(y.iloc[: loc + 1].values, add_constant(t[: loc + 1])).fit()
    post = OLS(y.iloc[loc + 1 :].values, add_constant(t[loc + 1 :])).fit()
    k = x_full.shape[1]
    ssr_pooled = full.ssr
    ssr_split = pre.ssr + post.ssr
    denom_df = len(y) - 2 * k
    if denom_df <= 0 or ssr_split <= 0:
        return {"break_date": str(bdate.date()), "f_stat": np.nan, "pvalue": np.nan, "nobs": len(y), "note": "singular"}
    f_stat = ((ssr_pooled - ssr_split) / k) / (ssr_split / denom_df)
    pvalue = 1 - stats.f.cdf(f_stat, k, denom_df)
    return {"break_date": str(bdate.date()), "f_stat": f_stat, "pvalue": pvalue, "nobs": len(y), "note": ""}


break_dates = ["2008-12-31", "2012-09-30", "2020-06-30", "2022-09-30"]
break_rows = []
event_rows = []
for var in LEVEL_TEST_VARIABLES:
    if var not in q.columns:
        continue
    series, transform = preferred_level(q, var)
    for bd in break_dates:
        result = chow_break(series, bd)
        result.update({"variable": var, "transform": transform})
        break_rows.append(result)
    growth = series.diff().dropna()
    pre_2020 = growth.loc[: "2019-12-31"]
    if len(pre_2020) >= 12 and pre_2020.std(ddof=1) > 0:
        for bd in break_dates:
            ts = pd.Timestamp(bd)
            if ts in growth.index:
                z = (growth.loc[ts] - pre_2020.mean()) / pre_2020.std(ddof=1)
                event_rows.append(
                    {
                        "variable": var,
                        "transform": transform,
                        "event_date": bd,
                        "growth_or_diff_at_event": growth.loc[ts],
                        "pre_2020_mean": pre_2020.mean(),
                        "pre_2020_sd": pre_2020.std(ddof=1),
                        "event_zscore_vs_pre2020": z,
                    }
                )

pd.DataFrame(break_rows).to_csv(TABLE_DIR / "quarterly_trend_chow_breaks.csv", index=False)
pd.DataFrame(event_rows).to_csv(TABLE_DIR / "quarterly_event_growth_zscores.csv", index=False)


def transformed_frame(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    out = {}
    for var in variables:
        if var not in df.columns:
            continue
        s, transform = preferred_level(df, var)
        out[var if transform == "level" else f"ln_{var}"] = s
    return pd.DataFrame(out)


corr_vars = [
    "wx_shadow_rate",
    "dfr_eop",
    "hh_loans_ea_stock",
    "nfc_loans_ea_stock",
    "house_price_de_real",
    "compensation_ea20_real",
    "dax_real_de",
    "retail_de_chained_index",
    "hicp_de",
    "credit_standards_enterprise",
    "credit_standards_household",
]
corr_levels = transformed_frame(q, corr_vars).dropna(how="all")
corr_growth = corr_levels.diff()
corr_levels.corr(min_periods=24).to_csv(TABLE_DIR / "quarterly_preferred_level_correlations.csv")
corr_growth.corr(min_periods=24).to_csv(TABLE_DIR / "quarterly_preferred_growth_correlations.csv")

redundancy_rows = []
c = corr_levels.corr(min_periods=24)
for i, a in enumerate(c.columns):
    for b in c.columns[i + 1 :]:
        val = c.loc[a, b]
        if pd.notna(val) and abs(val) >= 0.9:
            redundancy_rows.append({"series_a": a, "series_b": b, "level_corr": val, "risk": "high level collinearity"})
cg = corr_growth.corr(min_periods=24)
for i, a in enumerate(cg.columns):
    for b in cg.columns[i + 1 :]:
        val = cg.loc[a, b]
        if pd.notna(val) and abs(val) >= 0.7:
            redundancy_rows.append({"series_a": a, "series_b": b, "level_corr": val, "risk": "high growth/difference correlation"})
pd.DataFrame(redundancy_rows).to_csv(TABLE_DIR / "redundancy_and_collinearity_flags.csv", index=False)

# Extra redundancy checks for policy and credit variables.
monthly_policy = m[["wx_shadow_rate", "dfr_eop", "dfr_avg", "hh_loans_ea_stock", "nfc_loans_ea_stock"]].dropna()
policy_corr = monthly_policy.corr()
policy_corr.to_csv(TABLE_DIR / "monthly_policy_credit_correlations_common_sample.csv")
annual_join = annual.join(q[["wx_shadow_rate", "dfr_eop", "hh_loans_ea_stock", "nfc_loans_ea_stock", "house_price_de_real"]], how="left")
annual_join.corr(min_periods=8).to_csv(TABLE_DIR / "annual_balance_sheet_correlations.csv")


def add_logs(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in df.columns:
        if col == "date":
            continue
        s = df[col]
        if pd.api.types.is_numeric_dtype(s) and (s.dropna() > 0).all():
            out[f"ln_{col}"] = np.log(s)
    return out


qlog = add_logs(q)

candidate_sets = {
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
    "credit_assets_demand_constructed": [
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
        "ln_retail_de_chained_index",
    ],
    "not_recommended_with_shadow_rate": [
        "wx_shadow_rate",
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
    ],
    "not_recommended_with_dfr": [
        "dfr_eop",
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
    ],
}


def johansen_for_set(name: str, cols: list[str]) -> tuple[list[dict], list[dict]]:
    data = qlog[cols].dropna()
# Wu-Xia ends before the full 2022Q3 quarter.
    if "wx_shadow_rate" in cols:
        data = data.loc[: "2022-06-30"]
    rows = []
    lag_rows = []
    if len(data) < max(36, len(cols) * 8):
        rows.append({"system": name, "error": f"too few observations: {len(data)}", "nobs": len(data), "variables": ",".join(cols)})
        return rows, lag_rows
    maxlags = min(4, max(1, math.floor(len(data) / (len(cols) * 6))))
    try:
        so = select_order(data, maxlags=maxlags, deterministic="ci")
        selected = {k: int(v) if pd.notna(v) else np.nan for k, v in so.selected_orders.items()}
        for lag in range(maxlags + 1):
            lag_rows.append(
                {
                    "system": name,
                    "k_ar_diff": lag,
                    "aic": so.ics["aic"][lag],
                    "bic": so.ics["bic"][lag],
                    "hqic": so.ics["hqic"][lag],
                    "fpe": so.ics["fpe"][lag],
                    "selected_aic": selected.get("aic"),
                    "selected_bic": selected.get("bic"),
                    "selected_hqic": selected.get("hqic"),
                    "nobs": len(data),
                    "sample_start": data.index.min().date(),
                    "sample_end": data.index.max().date(),
                    "variables": ",".join(cols),
                }
            )
    except Exception as exc:
        selected = {"aic": 1, "bic": 1, "hqic": 1}
        lag_rows.append({"system": name, "error": str(exc), "nobs": len(data), "variables": ",".join(cols)})
    test_lags = sorted(set([1, 2, selected.get("bic", 1), selected.get("hqic", 1), selected.get("aic", 1)]))
    test_lags = [lag for lag in test_lags if isinstance(lag, (int, np.integer)) and lag >= 1 and lag <= max(1, maxlags)]
    for det_order in [-1, 0, 1]:
        for lag in test_lags:
            try:
                joh = coint_johansen(data, det_order=det_order, k_ar_diff=lag)
                trace_rank = select_coint_rank(data, det_order=det_order, k_ar_diff=lag, method="trace", signif=0.05).rank
                maxeig_rank = select_coint_rank(data, det_order=det_order, k_ar_diff=lag, method="maxeig", signif=0.05).rank
                for r in range(len(cols)):
                    rows.append(
                        {
                            "system": name,
                            "nobs": len(data),
                            "sample_start": data.index.min().date(),
                            "sample_end": data.index.max().date(),
                            "variables": ",".join(cols),
                            "det_order": det_order,
                            "k_ar_diff": lag,
                            "r_null": r,
                            "trace_stat": joh.lr1[r],
                            "trace_crit_95": joh.cvt[r, 1],
                            "trace_reject_95": bool(joh.lr1[r] > joh.cvt[r, 1]),
                            "maxeig_stat": joh.lr2[r],
                            "maxeig_crit_95": joh.cvm[r, 1],
                            "maxeig_reject_95": bool(joh.lr2[r] > joh.cvm[r, 1]),
                            "selected_trace_rank_5pct": int(trace_rank),
                            "selected_maxeig_rank_5pct": int(maxeig_rank),
                            "error": "",
                        }
                    )
            except Exception as exc:
                rows.append(
                    {
                        "system": name,
                        "nobs": len(data),
                        "sample_start": data.index.min().date() if len(data) else None,
                        "sample_end": data.index.max().date() if len(data) else None,
                        "variables": ",".join(cols),
                        "det_order": det_order,
                        "k_ar_diff": lag,
                        "error": str(exc),
                    }
                )
    return rows, lag_rows


coint_rows = []
lag_rows = []
for system_name, columns in candidate_sets.items():
    rows, lags = johansen_for_set(system_name, columns)
    coint_rows.extend(rows)
    lag_rows.extend(lags)

pd.DataFrame(coint_rows).to_csv(TABLE_DIR / "johansen_candidate_rank_sensitivity.csv", index=False)
pd.DataFrame(lag_rows).to_csv(TABLE_DIR / "vecm_lag_selection_candidates.csv", index=False)

# Research-readiness summary for candidate variables.
readiness = []
preferred_lookup = preferred_rows.set_index("variable")["classification"].to_dict()
recommendations = {
    "wx_shadow_rate": "primary monetary stance for 2004-09 to 2022-08; use as policy/shock variable, not cointegration level",
    "dfr_eop": "do not include with shadow rate; use as robustness/full-sample conventional-rate alternative",
    "ecb_total_assets": "exclude from core with current file; annual frequency is incompatible",
    "ecb_monetary_policy_securities": "exclude from core with current file; annual frequency is incompatible",
    "hh_loans_ea_stock": "retain; central household/asset-channel credit stock",
    "nfc_loans_ea_stock": "retain; central productive-credit stock",
    "credit_standards_enterprise": "use as exogenous/auxiliary mechanism variable, not VECM long-run level",
    "credit_standards_household": "use as exogenous/auxiliary mechanism variable, not VECM long-run level",
    "house_price_de_real": "retain; central real housing asset-price proxy",
    "house_price_de": "use only if model keeps an explicit price-level/HICP block",
    "compensation_ea20_real": "retain cautiously; purchasing-power proxy but geography mismatch",
    "retail_de_mom_pct": "exclude from VECM levels; stationary demand-growth robustness variable",
    "retail_de_chained_index": "exclude from core; constructed from growth, not official level",
    "dax_real_de": "include only in financial-asset robustness or expanded model; volatile and weak long-run anchor",
    "hicp_de": "use as deflator and possible inflation robustness variable; avoid duplicating real transformations",
    "hicp_ea20": "use as compensation deflator; avoid simultaneous inclusion with real compensation unless testing price-level channel",
}
for var, rec in recommendations.items():
    start = q[var].dropna().index.min().date() if var in q and q[var].notna().any() else None
    end = q[var].dropna().index.max().date() if var in q and q[var].notna().any() else None
    nobs = int(q[var].notna().sum()) if var in q else 0
    readiness.append(
        {
            "variable": var,
            "quarterly_nobs": nobs,
            "start": start,
            "end": end,
            "preferred_stationarity_classification": preferred_lookup.get(var, ""),
            "model_readiness_recommendation": rec,
        }
    )
pd.DataFrame(readiness).to_csv(TABLE_DIR / "variable_model_readiness.csv", index=False)

manifest = {
    "outputs": {
        "stationarity_quarterly_all_transforms": str(TABLE_DIR / "stationarity_quarterly_all_transforms.csv"),
        "stationarity_monthly_all_transforms": str(TABLE_DIR / "stationarity_monthly_all_transforms.csv"),
        "stationarity_quarterly_preferred_levels": str(TABLE_DIR / "stationarity_quarterly_preferred_levels.csv"),
        "breaks": str(TABLE_DIR / "quarterly_trend_chow_breaks.csv"),
        "event_zscores": str(TABLE_DIR / "quarterly_event_growth_zscores.csv"),
        "correlations": str(TABLE_DIR / "quarterly_preferred_level_correlations.csv"),
        "growth_correlations": str(TABLE_DIR / "quarterly_preferred_growth_correlations.csv"),
        "redundancy": str(TABLE_DIR / "redundancy_and_collinearity_flags.csv"),
        "johansen": str(TABLE_DIR / "johansen_candidate_rank_sensitivity.csv"),
        "lag_selection": str(TABLE_DIR / "vecm_lag_selection_candidates.csv"),
        "readiness": str(TABLE_DIR / "variable_model_readiness.csv"),
        "figures_dir": str(FIG_DIR),
    }
}
(TABLE_DIR / "diagnostics_manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
