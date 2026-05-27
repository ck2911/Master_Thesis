from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .first_stage import estimate_first_stage
from .horizon_design import complete_horizon_frame
from .inference import RegressionResult, coefficient_summary_row, fit_2sls, hac_bandwidth_for_horizon
from .specifications import (
    LPIVSpecification,
    REGIME_NAMES,
    RESULTS_ROOT,
    baseline_specification,
    prepare_lpiv_dataset,
    validate_specification_data,
)


@dataclass
class RegimeInteractionResult:
    specification: LPIVSpecification
    response: str
    horizon: int
    outcome: str
    sample: pd.DataFrame
    result: RegressionResult
    set_first_stage_f_stat: float
    set_first_stage_partial_r_squared: float

    def to_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for regime in REGIME_NAMES:
            coefficient_name = interaction_policy_column(self.specification.endogenous_policy, regime)
            if coefficient_name not in self.result.coefficients.index:
                continue
            row: dict[str, object] = {
                "specification": self.specification.name,
                "response": self.response,
                "horizon": self.horizon,
                "outcome": self.outcome,
                "regime": regime,
                "coefficient_name": coefficient_name,
                "nobs": self.result.nobs,
                "sample_start": self.sample["quarter"].min() if "quarter" in self.sample else "",
                "sample_end": self.sample["quarter"].max() if "quarter" in self.sample else "",
                "instrument": interaction_instrument_column(self.specification.instrument, regime),
                "hac_bandwidth": self.result.hac_bandwidth,
                "set_first_stage_f_stat": self.set_first_stage_f_stat,
                "set_first_stage_partial_r_squared": self.set_first_stage_partial_r_squared,
            }
            row.update(coefficient_summary_row(self.result, coefficient_name))
            row["cumulative_response"] = row["coefficient"]
            rows.append(row)
        return rows


def interaction_policy_column(policy_variable: str, regime: str) -> str:
    return f"{policy_variable}_x_{regime}"


def interaction_instrument_column(instrument: str, regime: str) -> str:
    return f"{instrument}_x_{regime}"


def add_regime_interactions(data: pd.DataFrame, spec: LPIVSpecification) -> tuple[pd.DataFrame, list[str], list[str]]:
    frame = data.copy()
    endogenous_columns: list[str] = []
    instrument_columns: list[str] = []
    for regime in REGIME_NAMES:
        regime_column = f"regime_{regime}"
        policy_column = interaction_policy_column(spec.endogenous_policy, regime)
        instrument_column = interaction_instrument_column(spec.instrument, regime)
        frame[policy_column] = frame[spec.endogenous_policy] * frame[regime_column]
        frame[instrument_column] = frame[spec.instrument] * frame[regime_column]
        endogenous_columns.append(policy_column)
        instrument_columns.append(instrument_column)
    return frame, endogenous_columns, instrument_columns


def estimate_regime_interaction_horizon(
    data: pd.DataFrame,
    spec: LPIVSpecification,
    response: str,
    horizon: int,
) -> RegimeInteractionResult:
    regime_columns = [f"regime_{regime}" for regime in REGIME_NAMES]
    frame, outcome, control_columns = complete_horizon_frame(
        data,
        response=response,
        horizon=horizon,
        controls=spec.resolved_control_variables(),
        control_lags=spec.control_lags,
        required_current=[spec.endogenous_policy, spec.instrument, *regime_columns],
    )
    frame, endogenous_columns, instrument_columns = add_regime_interactions(frame, spec)
    included_regime_controls = [f"regime_{regime}" for regime in REGIME_NAMES[1:]]
    exogenous_columns = [*control_columns, *included_regime_controls]
    x_columns = [*endogenous_columns, *exogenous_columns]
    z_columns = [*instrument_columns, *exogenous_columns]
    bandwidth = hac_bandwidth_for_horizon(horizon)
    result = fit_2sls(frame[outcome], x=frame[x_columns], z=frame[z_columns], hac_bandwidth=bandwidth)
    set_first_stage = estimate_first_stage(
        frame,
        policy_variable=spec.endogenous_policy,
        instruments=spec.instrument,
        controls=exogenous_columns,
        hac_bandwidth=bandwidth,
    )
    return RegimeInteractionResult(
        specification=spec,
        response=response,
        horizon=horizon,
        outcome=outcome,
        sample=frame,
        result=result,
        set_first_stage_f_stat=set_first_stage.f_statistic,
        set_first_stage_partial_r_squared=set_first_stage.partial_r_squared,
    )


def estimate_regime_interactions(
    spec: LPIVSpecification,
    data: pd.DataFrame | None = None,
) -> list[RegimeInteractionResult]:
    frame = data.copy() if data is not None else prepare_lpiv_dataset(spec)
    validate_specification_data(frame, spec)
    results: list[RegimeInteractionResult] = []
    for response in spec.responses:
        for horizon in spec.horizons:
            results.append(estimate_regime_interaction_horizon(frame, spec, response, horizon))
    return results


def regime_results_to_frame(results: list[RegimeInteractionResult]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for result in results:
        rows.extend(result.to_rows())
    return pd.DataFrame(rows)


def write_regime_outputs(results: list[RegimeInteractionResult], spec: LPIVSpecification) -> pd.DataFrame:
    table = regime_results_to_frame(results)
    target = RESULTS_ROOT / "regime"
    target.mkdir(parents=True, exist_ok=True)
    table.to_csv(target / f"{spec.name}_regime_interactions.csv", index=False)
    try:
        table.to_excel(target / f"{spec.name}_regime_interactions.xlsx", index=False)
    except ImportError:
        pass
    lines = [
        f"# Regime-Interaction LP-IV Check: {spec.name}",
        "",
        "Rows report regime-specific shock slopes from interaction LP-IVs.",
        "",
        f"- Regimes: {', '.join(REGIME_NAMES)}",
        f"- Response-horizon-regime rows: {table.shape[0]}",
    ]
    (target / f"{spec.name}_regime_interactions_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return table


def run_regime_pipeline(spec: LPIVSpecification | None = None) -> pd.DataFrame:
    active_spec = spec or baseline_specification()
    data = prepare_lpiv_dataset(active_spec)
    results = estimate_regime_interactions(active_spec, data=data)
    return write_regime_outputs(results, active_spec)
