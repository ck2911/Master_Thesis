# Final Repository Audit

Date: 2026-05-16

## Active Surface

- `notebooks/thesis_empirical_pipeline.ipynb`: thesis-facing interface.
- `scripts/run_full_pipeline.py`: canonical runner.
- `scripts/run_proxy_validation.py`: monthly proxy tournament.
- `scripts/run_information_effect_screening.py`: event contamination audit.
- `scripts/run_monthly_reduced_form_lp.py`: normalized reduced-form LP engine.
- `src/data/build_monthly_model_dataset.R`: monthly dataset builder with no quarterly interpolation.
- `src/lpiv/ols_hac.py`: local OLS/HAC helper used by final Python scripts.

## Final Output Tree

- `results/final/tables/`: normalized IRFs and cumulative outputs.
- `results/final/diagnostics/`: proxy validation, first-stage gate, and event screens.
- `results/final/regime/`: descriptive regime decomposition.
- `results/final/stability/`: subsample, rolling, and recursive stability outputs.
- `results/final/robustness/`: qualitative OLS comparison.
- `results/final/figures/`: monthly IRF SVGs and surprise diagnostics.

## Retired Architecture

The quarterly ECB-assets LP-IV architecture is retained only as archived history. The active causal object is the high-frequency ECB monetary-policy surprise, not ECB asset growth.

## Audit Status

The final empirical audit passed after the canonical monthly runner completed. The audit verifies required final outputs, proxy selections, event samples, reduced-form specification files, stability outputs, notebook surface, and forbidden claim patterns.

