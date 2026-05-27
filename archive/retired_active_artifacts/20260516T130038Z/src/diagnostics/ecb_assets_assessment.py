from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant

from src.cointegration.johansen import rank_sensitivity_table
from src.diagnostics.stationarity import stationarity_table


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "data" / "processed" / "eu_de" / "final_quarterly_model_dataset.csv"
DIAG_DIR = ROOT / "results" / "diagnostics"
STAT_DIR = ROOT / "results" / "stationarity"
COINT_DIR = ROOT / "results" / "cointegration"
FIG_DIR = ROOT / "results" / "diagnostics" / "figures"

for directory in (DIAG_DIR, STAT_DIR, COINT_DIR, FIG_DIR):
    directory.mkdir(parents=True, exist_ok=True)


BREAK_DATES = {
    "gfc_2008q4": "2008-12-31",
    "euro_crisis_2012q3": "2012-09-30",
    "qe_launch_2015q1": "2015-03-31",
    "covid_2020q2": "2020-06-30",
    "tightening_2022q3": "2022-09-30",
}

CORE_TARGETS = [
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_dax_real_de",
    "ln_compensation_ea20_real",
]


def load_master() -> pd.DataFrame:
    data = pd.read_csv(DATASET, parse_dates=["date"]).set_index("date").sort_index()
    return data


def plot_ecb_assets(data: pd.DataFrame) -> None:
    series = data["ecb_assets_ea_stock"].dropna()
    log_series = data["ln_ecb_assets_ea_stock"].dropna()
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    axes = axes.ravel()
    series.plot(ax=axes[0], title="ECB assets, EUR millions")
    log_series.plot(ax=axes[1], title="Log ECB assets")
    (100 * log_series.diff()).plot(ax=axes[2], title="Quarterly log growth, percent")
    (100 * log_series.diff(4)).plot(ax=axes[3], title="Four-quarter log growth, percent")
    for ax in axes:
        for date in BREAK_DATES.values():
            ax.axvline(pd.Timestamp(date), color="black", linewidth=0.8, alpha=0.25)
        ax.grid(True, alpha=0.25)
    fig.suptitle("ECB weekly central-bank assets aggregated to end-of-quarter stock")
    fig.savefig(FIG_DIR / "ecb_assets_quarterly_diagnostics.png", dpi=170)
    plt.close(fig)


def chow_break(series: pd.Series, break_date: str) -> dict[str, object]:
    y = series.dropna()
    bdate = pd.Timestamp(break_date)
    if bdate not in y.index:
        candidates = y.index[y.index <= bdate]
        if candidates.empty:
            return {"break_date": break_date, "f_stat": np.nan, "pvalue": np.nan, "note": "break before sample"}
        bdate = candidates.max()
    loc = y.index.get_loc(bdate)
    if loc < 8 or len(y) - loc - 1 < 8:
        return {"break_date": str(bdate.date()), "f_stat": np.nan, "pvalue": np.nan, "note": "insufficient pre/post observations"}
    t = np.arange(len(y))
    full = OLS(y.values, add_constant(t)).fit()
    pre = OLS(y.iloc[: loc + 1].values, add_constant(t[: loc + 1])).fit()
    post = OLS(y.iloc[loc + 1 :].values, add_constant(t[loc + 1 :])).fit()
    k = 2
    denom_df = len(y) - 2 * k
    ssr_split = pre.ssr + post.ssr
    f_stat = ((full.ssr - ssr_split) / k) / (ssr_split / denom_df)
    return {"break_date": str(bdate.date()), "f_stat": float(f_stat), "pvalue": float(1 - stats.f.cdf(f_stat, k, denom_df)), "note": ""}


def break_tables(data: pd.DataFrame) -> None:
    log_assets = data["ln_ecb_assets_ea_stock"].dropna()
    rows = []
    for break_id, date in BREAK_DATES.items():
        row = chow_break(log_assets, date)
        row["break_id"] = break_id
        row["variable"] = "ln_ecb_assets_ea_stock"
        rows.append(row)
    pd.DataFrame(rows).to_csv(DIAG_DIR / "ecb_assets_structural_break_tests.csv", index=False)

    growth = log_assets.diff()
    pre_2020 = growth.loc[: "2019-12-31"].dropna()
    event_rows = []
    for break_id, date in BREAK_DATES.items():
        ts = pd.Timestamp(date)
        if ts in growth.index:
            event_rows.append(
                {
                    "break_id": break_id,
                    "date": date,
                    "quarterly_log_growth": growth.loc[ts],
                    "pre_2020_mean": pre_2020.mean(),
                    "pre_2020_sd": pre_2020.std(ddof=1),
                    "zscore_vs_pre_2020": (growth.loc[ts] - pre_2020.mean()) / pre_2020.std(ddof=1),
                }
            )
    pd.DataFrame(event_rows).to_csv(DIAG_DIR / "ecb_assets_event_growth_zscores.csv", index=False)


def stationarity_outputs(data: pd.DataFrame) -> None:
    log_assets = data["ln_ecb_assets_ea_stock"]
    tests = pd.DataFrame(
        {
            "ln_ecb_assets_ea_stock": log_assets,
            "d_ln_ecb_assets_ea_stock": log_assets.diff(),
            "d4_ln_ecb_assets_ea_stock": log_assets.diff(4),
            "ecb_assets_ea_stock": data["ecb_assets_ea_stock"],
        }
    )
    stationarity_table(tests).to_csv(STAT_DIR / "ecb_assets_stationarity.csv", index=False)


def cointegration_outputs(data: pd.DataFrame) -> None:
    rows = []
    systems = {
        "liquidity_credit_housing_income_core": [
            "ln_ecb_assets_ea_stock",
            "ln_hh_loans_ea_stock",
            "ln_nfc_loans_ea_stock",
            "ln_house_price_de_real",
            "ln_compensation_ea20_real",
        ],
        "liquidity_credit_housing_income_dax": [
            "ln_ecb_assets_ea_stock",
            "ln_hh_loans_ea_stock",
            "ln_nfc_loans_ea_stock",
            "ln_house_price_de_real",
            "ln_compensation_ea20_real",
            "ln_dax_real_de",
        ],
    }
    for target in CORE_TARGETS:
        systems[f"liquidity_pair_{target}"] = ["ln_ecb_assets_ea_stock", target]

    baseline = data.loc[data["baseline_sample"] == True]  # noqa: E712
    robustness = data.loc[data["robustness_sample"] == True]  # noqa: E712
    for sample_name, sample_data in {"baseline": baseline, "robustness": robustness}.items():
        for system_name, variables in systems.items():
            available = sample_data[variables].dropna()
            if available.shape[0] < max(30, len(variables) * 8):
                rows.append(
                    {
                        "sample": sample_name,
                        "system": system_name,
                        "nobs": available.shape[0],
                        "variables": ",".join(variables),
                        "error": "too few observations for stable Johansen test",
                    }
                )
                continue
            ranks = rank_sensitivity_table(
                available,
                lag_values=[1, 2],
                det_orders=[-1, 0, 1],
                system_name=system_name,
            )
            ranks.insert(0, "sample", sample_name)
            rows.extend(ranks.to_dict("records"))
    pd.DataFrame(rows).to_csv(COINT_DIR / "ecb_assets_cointegration_diagnostics.csv", index=False)


def liquidity_strength(data: pd.DataFrame) -> None:
    baseline = data.loc[data["baseline_sample"] == True].copy()  # noqa: E712
    liquidity_growth = baseline["ln_ecb_assets_ea_stock"].diff()
    targets = {
        "hh_loans": ("ln_hh_loans_ea_stock", "credit"),
        "nfc_loans": ("ln_nfc_loans_ea_stock", "credit"),
        "real_house_prices": ("ln_house_price_de_real", "asset"),
        "real_dax": ("ln_dax_real_de", "asset"),
        "real_compensation": ("ln_compensation_ea20_real", "income"),
    }
    rows = []
    for label, (variable, channel) in targets.items():
        target_growth = baseline[variable].diff()
        target_yoy = baseline[variable].diff(4)
        for lead in range(0, 5):
            rows.append(
                {
                    "target": label,
                    "target_variable": variable,
                    "channel": channel,
                    "liquidity_growth": "quarterly_log_diff",
                    "target_growth": "quarterly_log_diff",
                    "target_lead_quarters": lead,
                    "correlation": liquidity_growth.corr(target_growth.shift(-lead)),
                }
            )
            rows.append(
                {
                    "target": label,
                    "target_variable": variable,
                    "channel": channel,
                    "liquidity_growth": "quarterly_log_diff",
                    "target_growth": "four_quarter_log_diff",
                    "target_lead_quarters": lead,
                    "correlation": liquidity_growth.corr(target_yoy.shift(-lead)),
                }
            )
    corr = pd.DataFrame(rows)
    corr.to_csv(DIAG_DIR / "liquidity_channel_strength_correlations.csv", index=False)

    summary = (
        corr.assign(abs_correlation=lambda x: x["correlation"].abs())
        .sort_values("abs_correlation", ascending=False)
        .groupby(["target", "target_variable", "channel"], as_index=False)
        .first()
    )
    channel_summary = summary.groupby("channel", as_index=False)["abs_correlation"].mean()
    summary.to_csv(DIAG_DIR / "liquidity_channel_strength_summary.csv", index=False)
    channel_summary.to_csv(DIAG_DIR / "liquidity_channel_strength_by_channel.csv", index=False)

    thesis_targets = {
        "real_house_prices": ("ln_house_price_de_real", "asset_housing"),
        "real_dax": ("ln_dax_real_de", "asset_equity"),
        "real_compensation": ("ln_compensation_ea20_real", "real_purchasing_power"),
    }
    focused_rows = []
    liquidity_yoy = baseline["ln_ecb_assets_ea_stock"].diff(4)
    for label, (variable, channel) in thesis_targets.items():
        target_yoy = baseline[variable].diff(4)
        for lead in range(0, 5):
            focused_rows.append(
                {
                    "target": label,
                    "target_variable": variable,
                    "channel": channel,
                    "target_lead_quarters": lead,
                    "four_quarter_growth_correlation": liquidity_yoy.corr(target_yoy.shift(-lead)),
                }
            )
    focused = pd.DataFrame(focused_rows)
    focused.to_csv(DIAG_DIR / "liquidity_asset_vs_income_four_quarter_test.csv", index=False)


def main() -> None:
    data = load_master()
    plot_ecb_assets(data)
    stationarity_outputs(data)
    break_tables(data)
    cointegration_outputs(data)
    liquidity_strength(data)
    print("ECB asset diagnostics written to results/diagnostics, results/stationarity, and results/cointegration.")


if __name__ == "__main__":
    main()
