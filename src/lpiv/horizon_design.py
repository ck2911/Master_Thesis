from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class HorizonOutcome:
    response: str
    horizon: int
    column: str


def horizon_column(response: str, horizon: int) -> str:
    return f"lp_{response}_h{horizon}"


def future_change(data: pd.DataFrame, response: str, horizon: int, anchor_lag: int = 1) -> pd.Series:
    """Construct the Jordà outcome y_{t+h} - y_{t-1}."""

    if horizon < 0:
        raise ValueError("LP horizons must be non-negative.")
    if response not in data.columns:
        raise KeyError(f"Response variable not found: {response}")
    return data[response].shift(-horizon) - data[response].shift(anchor_lag)


def add_horizon_outcomes(
    data: pd.DataFrame,
    responses: Iterable[str],
    horizons: Iterable[int],
    anchor_lag: int = 1,
) -> tuple[pd.DataFrame, list[HorizonOutcome]]:
    frame = data.copy()
    outcomes: list[HorizonOutcome] = []
    for response in responses:
        for horizon in horizons:
            column = horizon_column(response, horizon)
            frame[column] = future_change(frame, response, horizon, anchor_lag=anchor_lag)
            outcomes.append(HorizonOutcome(response=response, horizon=horizon, column=column))
    return frame, outcomes


def lagged_column(variable: str, lag: int) -> str:
    return f"L{lag}_{variable}"


def add_lagged_controls(
    data: pd.DataFrame,
    controls: Iterable[str],
    lags: int,
) -> tuple[pd.DataFrame, list[str]]:
    if lags < 0:
        raise ValueError("Control lag count must be non-negative.")
    frame = data.copy()
    control_columns: list[str] = []
    for variable in controls:
        if variable not in frame.columns:
            raise KeyError(f"Control variable not found: {variable}")
        for lag in range(1, lags + 1):
            column = lagged_column(variable, lag)
            frame[column] = frame[variable].shift(lag)
            control_columns.append(column)
    return frame, control_columns


def complete_horizon_frame(
    data: pd.DataFrame,
    response: str,
    horizon: int,
    controls: Iterable[str],
    control_lags: int,
    required_current: Iterable[str],
) -> tuple[pd.DataFrame, str, list[str]]:
    frame = data.copy()
    outcome = horizon_column(response, horizon)
    frame[outcome] = future_change(frame, response, horizon)
    frame, control_columns = add_lagged_controls(frame, controls, control_lags)
    required = [outcome, *required_current, *control_columns]
    clean = frame.dropna(subset=required).copy()
    return clean, outcome, control_columns


def horizon_sample_summary(data: pd.DataFrame, outcome: str) -> dict[str, object]:
    clean = data.dropna(subset=[outcome])
    return {
        "nobs_available": int(clean.shape[0]),
        "sample_start": clean["quarter"].min() if "quarter" in clean and not clean.empty else "",
        "sample_end": clean["quarter"].max() if "quarter" in clean and not clean.empty else "",
    }
