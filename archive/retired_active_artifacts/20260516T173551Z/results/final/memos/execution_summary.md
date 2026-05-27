# Canonical Execution Summary

Finished at: 2026-05-16T17:35:11.832243+00:00

Canonical interface: `notebooks/thesis_empirical_pipeline.ipynb`.
Canonical outputs: `results/final/`.

## Pipeline Steps

1. Build canonical monthly model dataset - completed with exit code 0.
2. Run monthly first-stage tournament - completed with exit code 0.
3. Run information-effect screening - completed with exit code 0.
4. Run monthly reduced-form LP layer - completed with exit code 0.

## Empirical Visibility

- Baseline response-horizon cells: 30.
- First-stage F-statistic range: 0.0157 to 0.2434.
- First-stage weak-IV flags: {'weak_iv_risk': 30}.
- Weak-IV classification counts: {'directional_only': 30}.
- Top ranked directional channels: NFC credit, Housing, HH credit.
- Monthly first-stage top bridge: d_dfr_eop via target_factor_monthly_easing (F=17.072093684754748, status=fragile_candidate).
- Monthly reduced-form LP cells: 150.

Hard-IV treatment interpretation remains gated. The active rebuild interpretation is monthly reduced-form and identification-bounded.
