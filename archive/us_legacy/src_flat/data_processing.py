from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from .config import LEGACY_DATASET, LEGACY_DATA_DIR, ROOT_POLICY_FILE, ROOT_SHOCK_FILE, SampleConfig


Aggregation = Literal["last", "mean"]


@dataclass(frozen=True)
class VariableTransformation:
    variable: str
    source: str
    transformation: str
    economic_role: str
    thesis_status: str


LEGACY_VARIABLE_MANIFEST = (
    VariableTransformation(
        variable="shadow_rate",
        source="Krippner U.S. shadow short rate, local workbook",
        transformation="Monthly level in percentage points",
        economic_role="Monetary policy stance / financial conditions",
        thesis_status="Legacy only: U.S./Fed proxy, not Germany/ECB",
    ),
    VariableTransformation(
        variable="ln_credit",
        source="FRED TOTBKCR, all U.S. commercial bank credit",
        transformation="Monthly mean, log level",
        economic_role="Financial intermediation",
        thesis_status="Legacy only: U.S. banking aggregate",
    ),
    VariableTransformation(
        variable="ln_real_equity",
        source="FRED NASDAQ100 and CPIAUCSL",
        transformation="Month-end equity index deflated by CPI, log level",
        economic_role="Asset prices, equity channel",
        thesis_status="Legacy only: U.S. equity proxy",
    ),
    VariableTransformation(
        variable="ln_real_housing",
        source="FRED CSUSHPINSA and CPIAUCSL",
        transformation="Monthly house price index deflated by CPI, log level",
        economic_role="Asset prices, housing channel",
        thesis_status="Legacy only: U.S. housing proxy",
    ),
    VariableTransformation(
        variable="ln_real_income",
        source="FRED DSPIC96",
        transformation="Real disposable personal income, log level",
        economic_role="Real economy / income channel",
        thesis_status="Legacy only: U.S. real income proxy",
    ),
    VariableTransformation(
        variable="ln_cpi",
        source="FRED CPIAUCSL",
        transformation="CPI, log level",
        economic_role="Inflation / price-level dynamics",
        thesis_status="Legacy only: U.S. inflation proxy",
    ),
)


def monthly_index(sample: SampleConfig) -> pd.DatetimeIndex:
    return pd.date_range(sample.start, sample.end, freq=sample.freq)


def _read_excel_series(
    path: Path,
    sheet_name: str,
    date_col: str,
    value_col: str,
    sample: SampleConfig,
    aggregation: Aggregation = "last",
) -> pd.Series:
    df = pd.read_excel(path, sheet_name=sheet_name, usecols=[date_col, value_col])
    df = df.dropna(subset=[date_col])
    df[date_col] = pd.to_datetime(df[date_col])
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    series = df.set_index(date_col)[value_col].sort_index()
    series = series.loc[sample.start : sample.end]
    resampler = series.resample(sample.freq)
    if aggregation == "mean":
        series = resampler.mean()
    else:
        series = resampler.last()
    return series.rename(value_col)


def _read_root_policy_series(sample: SampleConfig) -> pd.Series:
    if not ROOT_POLICY_FILE.exists():
        raise FileNotFoundError(
            f"Missing root-level policy file: {ROOT_POLICY_FILE}. "
            "Copy the SSR workbook to the project root or replace the legacy loader."
        )
    return _read_excel_series(
        ROOT_POLICY_FILE,
        sheet_name="Refined",
        date_col="DATES",
        value_col="US SSR",
        sample=sample,
        aggregation="last",
    ).rename("shadow_rate")


def _load_extracted_legacy_raw(sample: SampleConfig) -> pd.DataFrame:
    path = LEGACY_DATA_DIR / "legacy_raw_aligned.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing extracted legacy data file: {path}. "
            "Main_Files has been retired; use the extracted CSV instead."
        )
    raw = pd.read_csv(path, index_col=0, parse_dates=True)
    raw = raw.loc[sample.start : sample.end]
    return raw.reindex(monthly_index(sample))


def load_legacy_raw_data(sample: SampleConfig) -> pd.DataFrame:
    """Load the extracted U.S. data from the retired notebooks.

    Main_Files is deliberately no longer a dependency. The non-policy macro
    variables are preserved as an extracted aligned CSV under data/legacy_us,
    and the policy/shock files are read from the project root.
    """

    raw = _load_extracted_legacy_raw(sample)
    raw["shadow_rate"] = _read_root_policy_series(sample)
    return raw.loc[sample.start : sample.end]


def transform_legacy_data(raw: pd.DataFrame) -> pd.DataFrame:
    required = ["shadow_rate", "credit", "equity", "housing_price", "real_income", "cpi"]
    missing = [col for col in required if col not in raw]
    if missing:
        raise ValueError(f"Missing required columns for transformation: {missing}")

    data = raw.copy()
    for col in ["credit", "equity", "housing_price", "real_income", "cpi"]:
        if (data[col].dropna() <= 0).any():
            raise ValueError(f"{col} contains non-positive values and cannot be logged.")

    data["real_equity"] = data["equity"] / data["cpi"]
    data["real_housing"] = data["housing_price"] / data["cpi"]
    data["ln_credit"] = np.log(data["credit"])
    data["ln_real_equity"] = np.log(data["real_equity"])
    data["ln_real_housing"] = np.log(data["real_housing"])
    data["ln_real_income"] = np.log(data["real_income"])
    data["ln_cpi"] = np.log(data["cpi"])

    transformed = data.loc[:, LEGACY_DATASET.transformed_columns].dropna()
    expected = pd.date_range(transformed.index.min(), transformed.index.max(), freq="ME")
    missing_months = expected.difference(transformed.index)
    if not missing_months.empty:
        transformed = transformed.loc[: missing_months.min() - pd.offsets.MonthEnd(1)]
    return transformed.asfreq("ME")


def load_legacy_shocks(sample: SampleConfig) -> pd.DataFrame:
    if not ROOT_SHOCK_FILE.exists():
        raise FileNotFoundError(
            f"Missing root-level shock file: {ROOT_SHOCK_FILE}. "
            "Copy the JK shock CSV to the project root or replace the legacy loader."
        )
    shocks = pd.read_csv(ROOT_SHOCK_FILE)
    shocks["date"] = pd.to_datetime(
        shocks["year"].astype(str) + "-" + shocks["month"].astype(str) + "-01"
    ) + pd.offsets.MonthEnd(0)
    shocks = shocks.set_index("date").sort_index()
    shocks = shocks.loc[sample.start : sample.end]
    return shocks


def data_integrity_report(raw: pd.DataFrame, transformed: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, frame in [("raw", raw), ("transformed", transformed)]:
        for col in frame.columns:
            series = frame[col]
            rows.append(
                {
                    "dataset": label,
                    "variable": col,
                    "start": series.dropna().index.min(),
                    "end": series.dropna().index.max(),
                    "observations": int(series.notna().sum()),
                    "missing": int(series.isna().sum()),
                    "missing_share": float(series.isna().mean()),
                    "min": float(series.min(skipna=True)),
                    "max": float(series.max(skipna=True)),
                }
            )
    return pd.DataFrame(rows)


def variable_manifest() -> pd.DataFrame:
    return pd.DataFrame([item.__dict__ for item in LEGACY_VARIABLE_MANIFEST])
