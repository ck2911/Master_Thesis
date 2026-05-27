from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .first_stage import (
    FirstStageResult,
    estimate_first_stage,
    regime_relevance,
    rolling_relevance,
    write_first_stage_outputs,
)
from .horizon_design import add_lagged_controls, complete_horizon_frame
from .inference import RegressionResult, coefficient_summary_row, fit_2sls, hac_bandwidth_for_horizon
from .specifications import (
    LPIVSpecification,
    RESULTS_ROOT,
    baseline_specification,
    ensure_results_directories,
    output_directory,
    prepare_lpiv_dataset,
    validate_specification_data,
)


@dataclass
class LPIVHorizonResult:
    specification: LPIVSpecification
    response: str
    horizon: int
    outcome: str
    controls: tuple[str, ...]
    sample: pd.DataFrame
    iv_result: RegressionResult
    first_stage: FirstStageResult

    def to_row(self) -> dict[str, object]:
        coefficient = coefficient_summary_row(self.iv_result, self.specification.endogenous_policy)
        row: dict[str, object] = {
            "specification": self.specification.name,
            "response": self.response,
            "horizon": self.horizon,
            "outcome": self.outcome,
            "sample_window": self.specification.sample.name,
            "nobs": self.iv_result.nobs,
            "sample_start": self.sample["quarter"].min() if "quarter" in self.sample else "",
            "sample_end": self.sample["quarter"].max() if "quarter" in self.sample else "",
            "endogenous_policy": self.specification.endogenous_policy,
            "instrument": self.specification.instrument,
            "hac_bandwidth": self.iv_result.hac_bandwidth,
            "iv_r_squared": self.iv_result.r_squared,
            "first_stage_f_stat": self.first_stage.f_statistic,
            "first_stage_partial_r_squared": self.first_stage.partial_r_squared,
            "first_stage_nobs": self.first_stage.nobs,
            "control_lags": self.specification.control_lags,
            "controls": ",".join(self.controls),
        }
        row.update(coefficient)
        row["cumulative_response"] = row["coefficient"]
        return row


def estimate_lpiv_horizon(
    data: pd.DataFrame,
    spec: LPIVSpecification,
    response: str,
    horizon: int,
) -> LPIVHorizonResult:
    controls = spec.resolved_control_variables()
    frame, outcome, control_columns = complete_horizon_frame(
        data,
        response=response,
        horizon=horizon,
        controls=controls,
        control_lags=spec.control_lags,
        required_current=[spec.endogenous_policy, spec.instrument],
    )
    hac_bandwidth = hac_bandwidth_for_horizon(horizon)
    first_stage = estimate_first_stage(
        frame,
        policy_variable=spec.endogenous_policy,
        instruments=spec.instrument,
        controls=control_columns,
        hac_bandwidth=hac_bandwidth,
    )
    x_columns = [spec.endogenous_policy, *control_columns]
    z_columns = [spec.instrument, *control_columns]
    iv_result = fit_2sls(
        frame[outcome],
        x=frame[x_columns],
        z=frame[z_columns],
        hac_bandwidth=hac_bandwidth,
    )
    return LPIVHorizonResult(
        specification=spec,
        response=response,
        horizon=horizon,
        outcome=outcome,
        controls=tuple(control_columns),
        sample=frame,
        iv_result=iv_result,
        first_stage=first_stage,
    )


def estimate_specification(
    spec: LPIVSpecification,
    data: pd.DataFrame | None = None,
) -> list[LPIVHorizonResult]:
    frame = data.copy() if data is not None else prepare_lpiv_dataset(spec)
    validate_specification_data(frame, spec)
    results: list[LPIVHorizonResult] = []
    for response in spec.responses:
        for horizon in spec.horizons:
            results.append(estimate_lpiv_horizon(frame, spec, response, horizon))
    return results


def results_to_frame(results: list[LPIVHorizonResult]) -> pd.DataFrame:
    return pd.DataFrame([result.to_row() for result in results])


def write_lpiv_outputs(results: list[LPIVHorizonResult], spec: LPIVSpecification) -> pd.DataFrame:
    ensure_results_directories()
    table = results_to_frame(results)
    directory = output_directory(spec)
    csv_path = directory / f"{spec.name}_lpiv_coefficients.csv"
    table.to_csv(csv_path, index=False)
    table.to_csv(directory.parent / "tables" / f"{spec.name}_lpiv_coefficients.csv", index=False)
    try:
        table.to_excel(directory / f"{spec.name}_lpiv_coefficients.xlsx", index=False)
    except ImportError:
        pass
    write_lpiv_summary(table, spec, directory / f"{spec.name}_lpiv_summary.md")
    return table


def write_lpiv_summary(table: pd.DataFrame, spec: LPIVSpecification, path: Path) -> None:
    lines = [
        f"# LP-IV Estimation Check: {spec.name}",
        "",
        "This records estimation coverage and first-stage quality. It does not interpret thesis results.",
        "",
        f"- Sample: `{spec.sample.start}` to `{spec.sample.end}`",
        f"- Endogenous policy variable: `{spec.endogenous_policy}`",
        f"- Instrument: `{spec.instrument}`",
        f"- Responses: {len(spec.responses)}",
        f"- Horizons: {', '.join(str(horizon) for horizon in spec.horizons)}",
        f"- Control lags: {spec.control_lags}",
    ]
    if not table.empty:
        lines.extend(
            [
                "",
                "## Coverage",
                "",
                f"- Estimated response-horizon cells: {table.shape[0]}",
                f"- Minimum observations: {int(table['nobs'].min())}",
                f"- Maximum observations: {int(table['nobs'].max())}",
                f"- Minimum horizon-specific first-stage F-statistic: {table['first_stage_f_stat'].min():.3f}",
                f"- Maximum horizon-specific first-stage F-statistic: {table['first_stage_f_stat'].max():.3f}",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def first_stage_diagnostic_bundle(spec: LPIVSpecification, data: pd.DataFrame | None = None) -> None:
    frame = data.copy() if data is not None else prepare_lpiv_dataset(spec)
    validate_specification_data(frame, spec)
    frame, control_columns = add_lagged_controls(frame, spec.resolved_control_variables(), spec.control_lags)
    baseline = estimate_first_stage(
        frame,
        policy_variable=spec.endogenous_policy,
        instruments=spec.instrument,
        controls=control_columns,
        hac_bandwidth=1,
    )
    rolling = rolling_relevance(
        frame,
        policy_variable=spec.endogenous_policy,
        instrument=spec.instrument,
        controls=control_columns,
    )
    regimes = regime_relevance(
        frame,
        policy_variable=spec.endogenous_policy,
        instrument=spec.instrument,
        controls=control_columns,
    )
    write_first_stage_outputs(baseline, rolling, regimes, prefix=spec.name)


def run_lpiv_pipeline(spec: LPIVSpecification) -> pd.DataFrame:
    data = prepare_lpiv_dataset(spec)
    first_stage_diagnostic_bundle(spec, data=data)
    results = estimate_specification(spec, data=data)
    table = write_lpiv_outputs(results, spec)
    try:
        from .diagnostics import write_diagnostics_outputs

        write_diagnostics_outputs(results, spec, data=data)
    except Exception as exc:  # pragma: no cover - diagnostics should not block coefficient tables.
        diagnostic_note = output_directory(spec) / f"{spec.name}_diagnostics_note.md"
        diagnostic_note.write_text(f"Diagnostics generation skipped: {exc}\n", encoding="utf-8")
    try:
        from .regime_interactions import estimate_regime_interactions, write_regime_outputs

        write_regime_outputs(estimate_regime_interactions(spec, data=data), spec)
    except Exception as exc:  # pragma: no cover - regime output should not block baseline tables.
        regime_note = output_directory(spec) / f"{spec.name}_regime_note.md"
        regime_note.write_text(f"Regime interaction generation skipped: {exc}\n", encoding="utf-8")
    try:
        from .plotting import write_irf_svgs

        write_irf_svgs(table, output_dir=RESULTS_ROOT / "plots" / spec.name)
    except Exception as exc:  # pragma: no cover - plotting should never block tables.
        plot_note = output_directory(spec) / f"{spec.name}_plotting_note.md"
        plot_note.write_text(f"IRF plot generation skipped: {exc}\n", encoding="utf-8")
    return table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the LP-IV response estimates.")
    parser.add_argument(
        "--spec",
        choices=["baseline"],
        default="baseline",
        help="Specification to estimate.",
    )
    parser.add_argument(
        "--control-lags",
        type=int,
        default=None,
        help="Override the specification's control lag count.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec = baseline_specification()
    if args.control_lags is not None:
        spec = spec.with_updates(control_lags=args.control_lags)
    table = run_lpiv_pipeline(spec)
    print(f"LP-IV estimates complete: {table.shape[0]} response-horizon cells estimated.")


if __name__ == "__main__":
    main()
