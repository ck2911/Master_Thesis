#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FINAL_ROOT = RESULTS / "final"
ARCHIVE_ROOT = ROOT / "archive" / "retired_active_artifacts"
CANONICAL_NOTEBOOK = ROOT / "1. thesis_master_notebook.ipynb"
CANONICAL_NOTEBOOK_REL = CANONICAL_NOTEBOOK.relative_to(ROOT).as_posix()

FINAL_DIRS = {
    "figures": FINAL_ROOT / "figures",
    "tables": FINAL_ROOT / "tables",
    "diagnostics": FINAL_ROOT / "diagnostics",
    "robustness": FINAL_ROOT / "robustness",
    "regime": FINAL_ROOT / "regime",
    "stability": FINAL_ROOT / "stability",
    "uncertainty": FINAL_ROOT / "uncertainty",
    "mechanism": FINAL_ROOT / "mechanism",
    "proxy_validation": FINAL_ROOT / "proxy_validation",
    "proxy_validation_compensation": FINAL_ROOT / "proxy_validation" / "compensation",
    "memos": FINAL_ROOT / "memos",
    "figures_baseline": FINAL_ROOT / "figures" / "baseline",
    "figures_cumulative": FINAL_ROOT / "figures" / "cumulative",
    "figures_uncertainty": FINAL_ROOT / "figures" / "uncertainty",
    "figures_regimes": FINAL_ROOT / "figures" / "regimes",
    "figures_stability": FINAL_ROOT / "figures" / "stability",
    "figures_mechanism": FINAL_ROOT / "figures" / "mechanism",
    "figures_compensation": FINAL_ROOT / "figures" / "compensation",
    "figures_banking": FINAL_ROOT / "figures" / "banking",
}

RESPONSE_LABELS = {
    "ln_ecb_assets_ea_stock": "ECB assets",
    "ln_hh_loans_ea_stock": "HH credit",
    "ln_nfc_loans_ea_stock": "NFC credit",
    "ln_house_price_de_real": "Housing",
    "ln_compensation_ea20_real": "Compensation",
}

ACTIVE_OUTPUT_DIRS = (
    RESULTS / "lpiv",
    RESULTS / "diagnostics",
    RESULTS / "identification_rebuild",
    RESULTS / ".matplotlib",
    RESULTS / "stress_testing",
    RESULTS / "cointegration",
    RESULTS / "stationarity",
    RESULTS / "svecm",
    RESULTS / "irf",
    RESULTS / "robustness",
    RESULTS / "data_quality",
)

NONCANONICAL_DOCS = {
    "baseline_irf_interpretation_memo.md",
    "composite_instrument_design.md",
    "ecb_balance_sheet_forensic_assessment.md",
    "ecb_external_instrument_feasibility_memo.md",
    "ecb_external_instrument_pre_estimation_assessment.md",
    "ecb_surprise_aggregation_philosophy.md",
    "eu_de_restructuring_report.md",
    "final_data_source_registry.md",
    "final_estimation_protocol.md",
    "final_external_identification_recommendation.md",
    "final_model_blocks.md",
    "final_sample_window_documentation.md",
    "final_transformation_documentation.md",
    "germany_ecb_data_requirements.md",
    "lpiv_architecture.md",
    "lpiv_diagnostics_framework.md",
    "lpiv_identification_strategy.md",
    "lpiv_inference_design.md",
    "lpiv_regime_design.md",
    "methodology_notes.md",
    "pre_identification_system_assessment.md",
    "qe_vs_timing_identification_assessment.md",
    "regime_identification_stability.md",
    "repository_cleanup_report.md",
    "shock_weighting_design.md",
    "svecm_architecture_preparation_memo.md",
    "transmission_synthesis_framework.md",
    "variable_dictionary.csv",
    "weak_iv_structural_interpretation_memo.md",
}

CANONICAL_DOCS = {
    "project_map.md",
    "final_methodology.md",
    "final_claims_boundary.md",
    "final_causality_framework.md",
    "final_empirical_findings.md",
    "final_identification_statement.md",
    "final_delivery_report.md",
    "model_governance.md",
    "thesis_master_outline.md",
    "final_figure_registry.md",
    "final_table_registry.md",
    "source_to_claim_mapping.md",
    "results_hierarchy.md",
}


@dataclass
class StepResult:
    name: str
    returncode: int
    started_at: str
    finished_at: str
    command: list[str]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stamp() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def has_files(path: Path) -> bool:
    return path.exists() and any(child.is_file() for child in path.rglob("*"))


def archive_path(path: Path, archive_run: Path) -> None:
    if not path.exists():
        return
    destination = archive_run / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        suffix = stamp()
        destination = destination.with_name(f"{destination.name}_{suffix}")
    shutil.move(str(path), str(destination))


def archive_active_output_universes(archive_run: Path) -> None:
    for directory in ACTIVE_OUTPUT_DIRS:
        if directory.exists():
            archive_path(directory, archive_run)


def archive_previous_final(archive_run: Path) -> None:
    if has_files(FINAL_ROOT):
        archive_path(FINAL_ROOT, archive_run)


def archive_noncanonical_docs(archive_run: Path) -> None:
    docs_dir = ROOT / "docs"
    for name in NONCANONICAL_DOCS:
        path = docs_dir / name
        if path.exists():
            archive_path(path, archive_run)

    for path in docs_dir.iterdir() if docs_dir.exists() else []:
        if path.is_dir() or (path.is_file() and path.name not in CANONICAL_DOCS):
            archive_path(path, archive_run)


def archive_deprecated_code_and_runners(archive_run: Path) -> None:
    deprecated_paths = [
        ROOT / "src" / "svecm",
        ROOT / "src" / "cointegration",
        ROOT / "src" / "irf",
        ROOT / "src" / "transformations",
        ROOT / "src" / "plotting",
        ROOT / "src" / "diagnostics",
        ROOT / "scripts" / "run_eu_de_consolidation.sh",
        ROOT / "scripts" / "run_ecb_external_instrument_pipeline.sh",
        ROOT / "scripts" / "run_pre_identification_stress_tests.R",
        ROOT / "scripts" / "sanitize_hicp_extract.R",
        ROOT / "scripts" / "check_active_archive_firewall.py",
        ROOT / "scripts" / "run_canonical_baseline_lpiv.py",
        ROOT / "scripts" / "run_weak_iv_robustification.py",
        ROOT / "scripts" / "ingest_final_refinement_sources.py",
        ROOT / "scripts" / "rebuild_outputs.py",
        ROOT / "proxy_validation",
        ROOT / ".matplotlib_cache",
        ROOT / "notebooks",
    ]
    for path in deprecated_paths:
        if path.exists():
            archive_path(path, archive_run)

    for cache_dir in sorted(ROOT.rglob("__pycache__")):
        if "archive" not in cache_dir.relative_to(ROOT).parts:
            archive_path(cache_dir, archive_run)

    for ds_store in sorted(ROOT.rglob(".DS_Store")):
        if "archive" not in ds_store.relative_to(ROOT).parts:
            archive_path(ds_store, archive_run)


def ensure_final_dirs() -> None:
    for directory in FINAL_DIRS.values():
        directory.mkdir(parents=True, exist_ok=True)


def run_step(name: str, command: list[str], env: dict[str, str]) -> StepResult:
    started = utc_now()
    print(f"\n[{started.isoformat()}] {name}")
    print(" ".join(command))
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    finished = utc_now()
    if completed.returncode != 0:
        raise RuntimeError(f"{name} failed with exit code {completed.returncode}")
    return StepResult(
        name=name,
        returncode=completed.returncode,
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        command=command,
    )


def copy_if_exists(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_many(sources: list[tuple[Path, Path]]) -> None:
    for source, destination in sources:
        copy_if_exists(source, destination)


def consolidate_outputs() -> None:
    ensure_final_dirs()
    lpiv = RESULTS / "lpiv"
    ecb_diag = RESULTS / "diagnostics" / "ecb_monetary_surprises"

    table_files = [
        (lpiv / "canonical_baseline" / "baseline_summary_table.csv", FINAL_DIRS["tables"] / "baseline_summary_table.csv"),
        (lpiv / "cumulative_irfs" / "cumulative_irf_summary_table.csv", FINAL_DIRS["tables"] / "cumulative_irf_summary_table.csv"),
        (lpiv / "persistence" / "persistence_metrics.csv", FINAL_DIRS["tables"] / "persistence_metrics.csv"),
        (lpiv / "stability" / "sign_stability_matrix.csv", FINAL_DIRS["tables"] / "sign_stability_matrix.csv"),
        (lpiv / "stability" / "directional_consistency.csv", FINAL_DIRS["tables"] / "directional_consistency.csv"),
        (lpiv / "stability" / "persistence_consistency.csv", FINAL_DIRS["tables"] / "persistence_consistency.csv"),
        (lpiv / "stability" / "transmission_ranking.csv", FINAL_DIRS["tables"] / "final_transmission_ranking.csv"),
        (
            lpiv / "ols_comparison" / "tables" / "ols_vs_lpiv_structural_comparison.csv",
            FINAL_DIRS["tables"] / "ols_vs_lpiv_structural_comparison.csv",
        ),
    ]
    copy_many(table_files)

    diagnostic_files = [
        (
            lpiv / "canonical_baseline" / "horizon_first_stage_diagnostics.csv",
            FINAL_DIRS["diagnostics"] / "horizon_first_stage_diagnostics.csv",
        ),
        (
            lpiv / "weak_iv_validation" / "horizon_specific_relevance.csv",
            FINAL_DIRS["diagnostics"] / "horizon_specific_relevance.csv",
        ),
        (ecb_diag / "first_stage_relevance.csv", FINAL_DIRS["diagnostics"] / "first_stage_relevance.csv"),
        (ecb_diag / "event_coverage_by_regime.csv", FINAL_DIRS["diagnostics"] / "event_coverage_by_regime.csv"),
        (
            ecb_diag / "event_coverage_by_year_quarter_regime.csv",
            FINAL_DIRS["diagnostics"] / "event_coverage_by_year_quarter_regime.csv",
        ),
        (
            ecb_diag / "surprise_distribution_diagnostics.csv",
            FINAL_DIRS["diagnostics"] / "surprise_distribution_diagnostics.csv",
        ),
        (ecb_diag / "quarter_density_diagnostics.csv", FINAL_DIRS["diagnostics"] / "quarter_density_diagnostics.csv"),
        (ecb_diag / "information_effect_regime_summary.csv", FINAL_DIRS["diagnostics"] / "information_effect_regime_summary.csv"),
        (ecb_diag / "instrument_strength_matrix.csv", FINAL_DIRS["diagnostics"] / "instrument_strength_matrix.csv"),
        (
            RESULTS / "diagnostics" / "regime_specific_identification.csv",
            FINAL_DIRS["diagnostics"] / "regime_specific_identification.csv",
        ),
    ]
    copy_many(diagnostic_files)

    robustness_files = [
        (
            lpiv / "weak_iv_robust" / "tables" / "weak_iv_classification.csv",
            FINAL_DIRS["robustness"] / "weak_iv_classification.csv",
        ),
        (
            lpiv / "weak_iv_robust" / "baseline" / "baseline_ar_inference.csv",
            FINAL_DIRS["robustness"] / "baseline_ar_inference.csv",
        ),
        (
            lpiv / "weak_iv_robust" / "baseline" / "baseline_lpiv_coefficients.csv",
            FINAL_DIRS["robustness"] / "baseline_lpiv_coefficients.csv",
        ),
        (
            lpiv / "weak_iv_robust" / "weak_iv_method_note.md",
            FINAL_DIRS["robustness"] / "weak_iv_method_note.md",
        ),
        (
            lpiv / "weak_iv_validation" / "lag_robustness_1_2_4.csv",
            FINAL_DIRS["robustness"] / "lag_robustness_1_2_4.csv",
        ),
        (
            lpiv / "dax_robustness" / "baseline_vs_dax_augmented_comparison.csv",
            FINAL_DIRS["robustness"] / "baseline_vs_dax_augmented_comparison.csv",
        ),
    ]
    copy_many(robustness_files)

    regime_files = [
        (
            lpiv / "regime_irfs" / "regime_irf_summary_table.csv",
            FINAL_DIRS["regime"] / "regime_irf_summary_table.csv",
        ),
        (lpiv / "regime_irfs" / "regime_cumulative_irfs.csv", FINAL_DIRS["regime"] / "regime_cumulative_irfs.csv"),
        (lpiv / "regime_irfs" / "regime_comparison_table.csv", FINAL_DIRS["regime"] / "regime_comparison_table.csv"),
        (lpiv / "regime_irfs" / "regime_mutation_table.csv", FINAL_DIRS["regime"] / "regime_mutation_table.csv"),
        (
            lpiv / "weak_iv_robust" / "regime" / "regime_ar_diagnostics.csv",
            FINAL_DIRS["regime"] / "regime_ar_diagnostics.csv",
        ),
        (
            lpiv / "weak_iv_robust" / "regime" / "regime_full_window_robustness_ar_diagnostics.csv",
            FINAL_DIRS["regime"] / "regime_full_window_robustness_ar_diagnostics.csv",
        ),
    ]
    copy_many(regime_files)

    for response in RESPONSE_LABELS:
        copy_many(
            [
                (
                    lpiv / "canonical_baseline" / f"irf_{response}.png",
                    FINAL_DIRS["figures"] / f"baseline_irf_{response}.png",
                ),
                (
                    lpiv / "canonical_baseline" / f"irf_{response}.svg",
                    FINAL_DIRS["figures"] / f"baseline_irf_{response}.svg",
                ),
                (
                    lpiv / "cumulative_irfs" / f"cumulative_irf_{response}.png",
                    FINAL_DIRS["figures"] / f"cumulative_irf_{response}.png",
                ),
                (
                    lpiv / "cumulative_irfs" / f"cumulative_irf_{response}.svg",
                    FINAL_DIRS["figures"] / f"cumulative_irf_{response}.svg",
                ),
                (
                    lpiv / "weak_iv_robust" / "plots" / f"ar_encoded_irf_{response}.png",
                    FINAL_DIRS["figures"] / f"weak_iv_ar_encoded_{response}.png",
                ),
                (
                    lpiv / "regime_irfs" / f"regime_irf_{response}.png",
                    FINAL_DIRS["figures"] / f"regime_irf_{response}.png",
                ),
            ]
        )

    for response in (
        "ln_hh_loans_ea_stock",
        "ln_nfc_loans_ea_stock",
        "ln_house_price_de_real",
        "ln_compensation_ea20_real",
    ):
        copy_many(
            [
                (
                    lpiv / "ols_comparison" / "plots" / f"ols_vs_lpiv_{response}.png",
                    FINAL_DIRS["figures"] / f"ols_vs_lpiv_{response}.png",
                ),
                (
                    lpiv / "ols_comparison" / "plots" / f"ols_vs_lpiv_{response}.svg",
                    FINAL_DIRS["figures"] / f"ols_vs_lpiv_{response}.svg",
                ),
            ]
        )

    for response in (
        "ln_house_price_de_real",
        "ln_hh_loans_ea_stock",
        "ln_compensation_ea20_real",
    ):
        copy_many(
            [
                (
                    lpiv / "regime_irfs" / f"regime_cumulative_{response}.png",
                    FINAL_DIRS["figures"] / f"regime_cumulative_{response}.png",
                ),
                (
                    lpiv / "regime_irfs" / f"regime_cumulative_{response}.svg",
                    FINAL_DIRS["figures"] / f"regime_cumulative_{response}.svg",
                ),
            ]
        )

    copy_many(
        [
            (lpiv / "weak_iv_validation" / "fstat_paths.png", FINAL_DIRS["figures"] / "fstat_paths.png"),
            (
                ecb_diag / "figures" / "regime_histograms.png",
                FINAL_DIRS["figures"] / "instrument_regime_histograms.png",
            ),
            (
                ecb_diag / "figures" / "quarter_density.png",
                FINAL_DIRS["figures"] / "instrument_quarter_density.png",
            ),
            (
                ecb_diag / "figures" / "quarterly_surprise_rolling_variance.png",
                FINAL_DIRS["figures"] / "quarterly_surprise_rolling_variance.png",
            ),
        ]
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def count_statuses(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(column, "missing")
        counts[value] = counts.get(value, 0) + 1
    return counts


def write_execution_memos(step_results: list[StepResult], archive_run: Path) -> None:
    baseline_path = FINAL_DIRS["tables"] / "baseline_summary_table.csv"
    weak_path = FINAL_DIRS["robustness"] / "weak_iv_classification.csv"
    ranking_path = FINAL_DIRS["tables"] / "final_transmission_ranking.csv"
    first_stage_path = FINAL_DIRS["diagnostics"] / "horizon_first_stage_diagnostics.csv"
    monthly_tournament_path = FINAL_DIRS["diagnostics"] / "monthly_first_stage_tournament.csv"
    monthly_lp_path = FINAL_DIRS["tables"] / "monthly_reduced_form_lp_coefficients.csv"
    proxy_path = FINAL_DIRS["diagnostics"] / "proxy_validation_tournament.csv"
    stability_path = FINAL_DIRS["stability"] / "monthly_directional_stability_matrix.csv"

    baseline = read_csv(baseline_path) if baseline_path.exists() else []
    weak = read_csv(weak_path) if weak_path.exists() else []
    ranking = read_csv(ranking_path) if ranking_path.exists() else []
    first_stage = read_csv(first_stage_path) if first_stage_path.exists() else []
    monthly_tournament = read_csv(monthly_tournament_path) if monthly_tournament_path.exists() else []
    monthly_lp = read_csv(monthly_lp_path) if monthly_lp_path.exists() else []
    proxy_rows = read_csv(proxy_path) if proxy_path.exists() else []
    stability_rows = read_csv(stability_path) if stability_path.exists() else []

    weak_counts = count_statuses(weak, "weak_iv_robust_status")
    weak_flags = count_statuses(first_stage, "weak_iv_flag")
    min_f = min((float(row["F_stat"]) for row in first_stage if row.get("F_stat")), default=float("nan"))
    max_f = max((float(row["F_stat"]) for row in first_stage if row.get("F_stat")), default=float("nan"))
    min_f_json = None if min_f != min_f else min_f
    max_f_json = None if max_f != max_f else max_f

    top_channels = ", ".join(row.get("channel", row.get("response", "")) for row in ranking[:3])
    top_monthly_bridge = ""
    if monthly_tournament:
        top = monthly_tournament[0]
        top_monthly_bridge = (
            f"{top.get('target', '')} via {top.get('instrument', '')} "
            f"(F={top.get('first_stage_f_stat', '')}, status={top.get('final_screen', '')})"
        )
    finished = utc_now()
    summary = {
        "finished_at": finished.isoformat(),
        "canonical_notebook": CANONICAL_NOTEBOOK_REL,
        "canonical_output_root": "results/final",
        "archive_run": str(archive_run.relative_to(ROOT)),
        "baseline_cells": len(baseline),
        "weak_iv_status_counts": weak_counts,
        "first_stage_flag_counts": weak_flags,
        "first_stage_f_min": min_f_json,
        "first_stage_f_max": max_f_json,
        "top_ranked_channels": top_channels,
        "monthly_first_stage_top_bridge": top_monthly_bridge,
        "monthly_reduced_form_cells": len(monthly_lp),
        "proxy_validation_candidates": len(proxy_rows),
        "monthly_stability_cells": len(stability_rows),
        "steps": [result.__dict__ for result in step_results],
    }

    (FINAL_DIRS["memos"] / "execution_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Execution Summary",
        "",
        f"Main notebook: `{CANONICAL_NOTEBOOK_REL}`.",
        "Main outputs: `results/final/`.",
        "",
        "## Rebuild Steps",
        "",
    ]
    for index, result in enumerate(step_results, start=1):
        lines.append(f"{index}. {result.name} - completed with exit code {result.returncode}.")
    lines.extend(["", "## Empirical Outputs", ""])
    if baseline:
        lines.extend(
            [
                f"- Retired quarterly LP-IV response-horizon cells: {len(baseline)}.",
                f"- Retired quarterly first-stage F-statistic range: {min_f:.4f} to {max_f:.4f}.",
                f"- Retired quarterly weak-IV flags: {weak_flags}.",
                f"- Retired quarterly weak-IV classification counts: {weak_counts}.",
                f"- Retired quarterly top ranked channels: {top_channels}.",
            ]
        )
    else:
        lines.append("- Retired quarterly LP-IV layer was not run.")
    lines.extend(
        [
            f"- Monthly first-stage top bridge: {top_monthly_bridge or 'not available'}.",
            f"- Monthly reduced-form LP cells: {len(monthly_lp)}.",
            f"- Proxy candidates screened: {len(proxy_rows)}.",
            f"- Monthly stability matrix cells: {len(stability_rows)}.",
            "",
            "Hard-IV treatment claims remain gated. The thesis interpretation is monthly reduced-form and tied to the ECB policy-news shock.",
        ]
    )
    (FINAL_DIRS["memos"] / "execution_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    synthesis = [
        "# Empirical Synthesis",
        "",
        "The thesis uses monthly high-frequency ECB monetary-policy surprises rather than a quarterly ECB-assets IV treatment.",
        "",
        "The monthly first-stage screen does not support a hard-IV treatment bridge. The empirical layer is therefore reduced-form dynamic transmission from policy-news shocks.",
        "",
        "Housing and compensation are not interpolated into monthly data. The final comparison uses monthly housing-finance and real negotiated-wage-pressure proxies, with exact house-price, compensation, welfare, and redistribution magnitudes outside the claim boundary.",
    ]
    (FINAL_DIRS["memos"] / "final_empirical_synthesis.md").write_text("\n".join(synthesis) + "\n", encoding="utf-8")


def run_audit_step(env: dict[str, str]) -> StepResult:
    return run_step("Check final empirical outputs", [sys.executable, "scripts/final_empirical_audit.py"], env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild the thesis empirical results.")
    parser.add_argument("--skip-data", action="store_true", help="Do not rebuild processed data.")
    parser.add_argument("--skip-instrument", action="store_true", help="Do not rebuild ECB surprise inputs.")
    parser.add_argument("--skip-audit", action="store_true", help="Do not check final empirical outputs.")
    args = parser.parse_args()

    env = os.environ.copy()
    env["MPLCONFIGDIR"] = str(Path("/private/tmp") / "thesis_model_mpl_cache")
    archive_run = ARCHIVE_ROOT / stamp()
    archive_run.mkdir(parents=True, exist_ok=True)

    full_rebuild = not args.skip_data and not args.skip_instrument
    if full_rebuild:
        archive_previous_final(archive_run)
    else:
        ensure_final_dirs()
    archive_active_output_universes(archive_run)
    archive_deprecated_code_and_runners(archive_run)

    step_results: list[StepResult] = []
    try:
        if not args.skip_data:
            step_results.append(run_step("Rebuild processed EU/DE data", ["Rscript", "src/data/build_final_dataset.R"], env))
        if not args.skip_instrument:
            step_results.append(
                run_step("Build ECB external-instrument shocks", [sys.executable, "-m", "src.data.ecb_monetary_surprises"], env)
            )
        step_results.append(run_step("Build monthly model dataset", ["Rscript", "src/data/build_monthly_model_dataset.R"], env))
        step_results.append(run_step("Run monthly first-stage tournament", [sys.executable, "scripts/run_first_stage_tournament.py"], env))
        step_results.append(run_step("Run information-effect screening", [sys.executable, "scripts/run_information_effect_screening.py"], env))
        step_results.append(run_step("Screen monthly proxies", [sys.executable, "scripts/run_proxy_validation.py"], env))
        step_results.append(run_step("Run monthly reduced-form LP layer", [sys.executable, "scripts/run_monthly_reduced_form_lp.py"], env))

        consolidate_outputs()
        write_execution_memos(step_results, archive_run)
        archive_active_output_universes(archive_run)
        archive_noncanonical_docs(archive_run)
        archive_deprecated_code_and_runners(archive_run)

        if not args.skip_audit:
            step_results.append(run_audit_step(env))
            write_execution_memos(step_results, archive_run)
    except RuntimeError as exc:
        print(f"\nPipeline failed: {exc}", file=sys.stderr)
        return 1

    print("\nThesis empirical rebuild completed.")
    print(f"Final outputs: {FINAL_ROOT.relative_to(ROOT)}")
    print(f"Archived old outputs: {archive_run.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
