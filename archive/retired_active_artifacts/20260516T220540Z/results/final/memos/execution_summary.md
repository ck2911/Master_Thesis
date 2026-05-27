# Canonical Execution Summary

Finished at: 2026-05-16T22:05:24.176055+00:00

Canonical interface: `notebooks/thesis_empirical_pipeline.ipynb`.
Canonical outputs: `results/final/`.

## Pipeline Steps

1. Rebuild processed EU/DE data - completed with exit code 0.
2. Rebuild ECB external instrument pipeline - completed with exit code 0.
3. Build canonical monthly model dataset - completed with exit code 0.
4. Run monthly first-stage tournament - completed with exit code 0.
5. Run information-effect screening - completed with exit code 0.
6. Run monthly proxy validation tournament - completed with exit code 0.
7. Run monthly reduced-form LP layer - completed with exit code 0.

## Empirical Visibility

- Retired quarterly LP-IV layer was not run.
- Monthly first-stage top bridge: d_dfr_eop via target_factor_monthly_easing (F=17.072093684754776, status=fragile_candidate).
- Monthly reduced-form LP cells: 660.
- Proxy validation candidates: 18.
- Monthly stability matrix cells: 60.

Hard-IV treatment interpretation remains gated. The active rebuild interpretation is monthly reduced-form and identification-bounded.
