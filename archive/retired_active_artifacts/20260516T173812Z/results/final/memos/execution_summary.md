# Canonical Execution Summary

Finished at: 2026-05-16T17:37:08.110148+00:00

Canonical interface: `notebooks/thesis_empirical_pipeline.ipynb`.
Canonical outputs: `results/final/`.

## Pipeline Steps

1. Build canonical monthly model dataset - completed with exit code 0.
2. Run monthly first-stage tournament - completed with exit code 0.
3. Run information-effect screening - completed with exit code 0.
4. Run monthly reduced-form LP layer - completed with exit code 0.

## Empirical Visibility

- Retired quarterly LP-IV layer was not run.
- Monthly first-stage top bridge: d_dfr_eop via target_factor_monthly_easing (F=17.072093684754748, status=fragile_candidate).
- Monthly reduced-form LP cells: 150.

Hard-IV treatment interpretation remains gated. The active rebuild interpretation is monthly reduced-form and identification-bounded.
