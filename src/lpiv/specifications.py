from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "eu_de"
RESULTS_ROOT = PROJECT_ROOT / "results" / "lpiv"

CANONICAL_DATASET = PROCESSED_DIR / "final_quarterly_model_dataset.csv"
ECB_SURPRISE_QUARTERLY = PROCESSED_DIR / "ecb_surprise_quarterly.csv"

OFFICIAL_BASELINE_INSTRUMENT = "target_factor_market_magnitude_weighted_quarterly_sum"
ENDOGENOUS_POLICY_VARIABLE = "d_ecb_assets_ea_qavg"

DEFAULT_HORIZONS = (0, 1, 2, 4, 8, 12)

BASELINE_RESPONSES = (
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real",
)

BASELINE_CONTROL_VARIABLES = (
    "ln_ecb_assets_ea_stock",
    "ln_hh_loans_ea_stock",
    "ln_nfc_loans_ea_stock",
    "ln_house_price_de_real",
    "ln_compensation_ea20_real",
    "inflation_ea20_qoq",
    "policy_rate",
)

REGIME_NAMES = ("pre_qe", "qe", "covid", "tightening")
REGIME_WINDOWS = {
    "pre_qe": ("2005Q1", "2014Q1"),
    "qe": ("2014Q2", "2019Q4"),
    "covid": ("2020Q1", "2021Q4"),
    "tightening": ("2022Q1", "2025Q4"),
}

@dataclass(frozen=True)
class SampleWindow:
    name: str
    start: str
    end: str

    @property
    def start_timestamp(self) -> pd.Timestamp:
        return pd.Period(self.start, freq="Q").to_timestamp(how="end").normalize()

    @property
    def end_timestamp(self) -> pd.Timestamp:
        return pd.Period(self.end, freq="Q").to_timestamp(how="end").normalize()

    def mask(self, data: pd.DataFrame) -> pd.Series:
        dates = pd.to_datetime(data["date"])
        return dates.between(self.start_timestamp, self.end_timestamp)


BASELINE_SAMPLE = SampleWindow("baseline", "2005Q1", "2022Q2")
ROBUSTNESS_SAMPLE = SampleWindow("robustness", "2005Q1", "2025Q4")


@dataclass(frozen=True)
class LPIVSpecification:
    name: str
    sample: SampleWindow
    responses: tuple[str, ...]
    endogenous_policy: str = ENDOGENOUS_POLICY_VARIABLE
    instrument: str = OFFICIAL_BASELINE_INSTRUMENT
    horizons: tuple[int, ...] = DEFAULT_HORIZONS
    control_variables: tuple[str, ...] = BASELINE_CONTROL_VARIABLES
    control_lags: int = 2
    policy_rate_variable: str = "wx_shadow_rate"
    include_dax_control: bool = False
    output_subdir: str = "baseline"

    def resolved_control_variables(self) -> tuple[str, ...]:
        resolved: list[str] = []
        for variable in self.control_variables:
            if variable == "policy_rate":
                resolved.append(self.policy_rate_variable)
            else:
                resolved.append(variable)
        if self.include_dax_control and "ln_dax_real_de" not in resolved:
            resolved.append("ln_dax_real_de")
        return tuple(dict.fromkeys(resolved))

    def with_updates(self, **updates: object) -> "LPIVSpecification":
        return replace(self, **updates)


def baseline_specification(**updates: object) -> LPIVSpecification:
    spec = LPIVSpecification(
        name="baseline",
        sample=BASELINE_SAMPLE,
        responses=BASELINE_RESPONSES,
        horizons=DEFAULT_HORIZONS,
        policy_rate_variable="wx_shadow_rate",
        include_dax_control=False,
        output_subdir="baseline",
    )
    return spec.with_updates(**updates) if updates else spec


def ensure_results_directories() -> None:
    for path in [
        RESULTS_ROOT,
        RESULTS_ROOT / "baseline",
        RESULTS_ROOT / "robustness",
        RESULTS_ROOT / "regime",
        RESULTS_ROOT / "diagnostics",
        RESULTS_ROOT / "diagnostics" / "first_stage",
        RESULTS_ROOT / "plots",
        RESULTS_ROOT / "tables",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def _read_quarterly_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required LP-IV source file does not exist: {path}")
    data = pd.read_csv(path, parse_dates=["date"])
    if "quarter" not in data.columns:
        data["quarter"] = data["date"].dt.to_period("Q").astype(str)
    return data.sort_values("date").reset_index(drop=True)


def load_canonical_dataset(path: Path = CANONICAL_DATASET) -> pd.DataFrame:
    return _read_quarterly_csv(path)


def load_ecb_surprises(path: Path = ECB_SURPRISE_QUARTERLY) -> pd.DataFrame:
    return _read_quarterly_csv(path)


def quarter_regime(quarter: str | pd.Period) -> str:
    period = pd.Period(quarter, freq="Q") if not isinstance(quarter, pd.Period) else quarter
    for regime, (start, end) in REGIME_WINDOWS.items():
        if pd.Period(start, freq="Q") <= period <= pd.Period(end, freq="Q"):
            return regime
    return "outside_regime_windows"


def add_regime_indicators(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    periods = pd.PeriodIndex(frame["quarter"], freq="Q")
    frame["lpiv_regime"] = [quarter_regime(period) for period in periods]
    for regime in REGIME_NAMES:
        frame[f"regime_{regime}"] = frame["lpiv_regime"].eq(regime).astype(int)
    return frame


def add_required_transformations(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.sort_values("date").copy()
    if "ln_hicp_ea20" in frame.columns:
        frame["inflation_ea20_qoq"] = frame["ln_hicp_ea20"].diff()
    elif "hicp_ea20" in frame.columns:
        frame["inflation_ea20_qoq"] = np.log(frame["hicp_ea20"]).diff()
    else:
        raise KeyError("Canonical dataset is missing `ln_hicp_ea20` or `hicp_ea20` for inflation controls.")

    if ENDOGENOUS_POLICY_VARIABLE not in frame.columns:
        if "ecb_assets_ea_qavg" not in frame.columns:
            raise KeyError("Canonical dataset is missing `ecb_assets_ea_qavg` for the LP-IV policy variable.")
        frame[ENDOGENOUS_POLICY_VARIABLE] = frame["ecb_assets_ea_qavg"].diff()

    for column in [
        "ln_ecb_assets_ea_stock",
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
        "ln_dax_real_de",
    ]:
        if column in frame.columns:
            frame[f"d_{column}"] = frame[column].diff()
    return frame


def prepare_lpiv_dataset(
    spec: LPIVSpecification,
    canonical_path: Path = CANONICAL_DATASET,
    surprise_path: Path = ECB_SURPRISE_QUARTERLY,
) -> pd.DataFrame:
    canonical = add_required_transformations(load_canonical_dataset(canonical_path))
    surprises = load_ecb_surprises(surprise_path)
    merged = canonical.merge(surprises, on=["date", "quarter"], how="left", suffixes=("", "_surprise"))
    merged = add_regime_indicators(merged)
    merged = merged.loc[spec.sample.mask(merged)].copy()
    return merged.reset_index(drop=True)


def require_columns(data: pd.DataFrame, columns: Iterable[str], context: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise KeyError(f"{context} is missing required columns: {missing}")


def validate_specification_data(data: pd.DataFrame, spec: LPIVSpecification) -> None:
    required = [
        spec.endogenous_policy,
        spec.instrument,
        *spec.responses,
        *spec.resolved_control_variables(),
    ]
    require_columns(data, required, f"LP-IV specification `{spec.name}`")


def output_directory(spec: LPIVSpecification) -> Path:
    ensure_results_directories()
    directory = RESULTS_ROOT / spec.output_subdir
    directory.mkdir(parents=True, exist_ok=True)
    return directory
