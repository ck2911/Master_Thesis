from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
LEGACY_DATA_DIR = DATA_DIR / "legacy_us"
ROOT_POLICY_FILE = PROJECT_ROOT / "1. SSR_estimates_M.xlsx"
ROOT_SHOCK_FILE = PROJECT_ROOT / "6. shocks_fed_jk_m.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"


@dataclass(frozen=True)
class SampleConfig:
    start: str = "2005-01-01"
    end: str = "2025-12-31"
    covid_split: str = "2020-03-31"
    freq: str = "ME"


@dataclass(frozen=True)
class LegacyDatasetConfig:
    """Fallback data extracted from the retired U.S. notebooks.

    This is a U.S./Fed system, so it is kept only for comparison with the
    Germany/euro-area thesis work.
    """

    name: str = "legacy_us"
    policy_column: str = "shadow_rate"
    shock_column: str = "MP_pm"
    transformed_columns: tuple[str, ...] = (
        "shadow_rate",
        "ln_credit",
        "ln_real_equity",
        "ln_real_housing",
        "ln_real_income",
        "ln_cpi",
    )


DEFAULT_SAMPLE = SampleConfig()
LEGACY_DATASET = LegacyDatasetConfig()


def ensure_output_dirs() -> None:
    for path in (RESULTS_DIR, TABLES_DIR, FIGURES_DIR, REPORTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
