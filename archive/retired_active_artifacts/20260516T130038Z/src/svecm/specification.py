from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DATASET = PROJECT_ROOT / "data" / "processed" / "eu_de" / "final_quarterly_model_dataset.csv"


@dataclass(frozen=True)
class SampleWindow:
    name: str
    start: str
    end: str
    policy_variable: str

    def trim(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.loc[pd.Timestamp(self.start) : pd.Timestamp(self.end)].copy()


BASELINE_SAMPLE = SampleWindow(
    name="baseline",
    start="2005-03-31",
    end="2022-06-30",
    policy_variable="wx_shadow_rate",
)

ROBUSTNESS_SAMPLE = SampleWindow(
    name="robustness",
    start="2005-03-31",
    end="2025-12-31",
    policy_variable="dfr_eop",
)

ENDOGENOUS_CORE = [
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real",
]

ENDOGENOUS_EXPANDED = [
    *ENDOGENOUS_CORE,
    "ln_dax_real_de",
]

BASELINE_EXOGENOUS = [
    "wx_shadow_rate",
    "credit_standards_enterprise",
    "credit_standards_household",
    "dummy_gfc_2008q4",
    "dummy_euro_crisis_2012q3",
    "dummy_qe_launch_2015q1",
    "dummy_covid_2020q2",
]

ROBUSTNESS_EXOGENOUS = [
    "dfr_eop",
    "credit_standards_enterprise",
    "credit_standards_household",
    "dummy_gfc_2008q4",
    "dummy_euro_crisis_2012q3",
    "dummy_qe_launch_2015q1",
    "dummy_covid_2020q2",
    "dummy_2022_tightening_q3",
]


def load_canonical_dataset(path: Path = CANONICAL_DATASET) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["date"])
    return data.set_index("date").sort_index()


def svecm_design_matrix(
    sample: SampleWindow = BASELINE_SAMPLE,
    endogenous: list[str] | None = None,
    exogenous: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return trimmed endogenous and exogenous matrices.

    The archived SVECM code keeps fixed EU/Germany sample windows so it does
    not fall back to older prototype assumptions.
    """

    data = sample.trim(load_canonical_dataset())
    endog_cols = endogenous or ENDOGENOUS_CORE
    exog_cols = exogenous or (BASELINE_EXOGENOUS if sample.name == "baseline" else ROBUSTNESS_EXOGENOUS)
    required = endog_cols + exog_cols
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise KeyError(f"Canonical dataset is missing required variables: {missing}")
    design = data[required].dropna()
    return design[endog_cols], design[exog_cols]
