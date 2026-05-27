# Canonical Execution Summary

Finished at: 2026-05-16T14:18:33.775388+00:00

Canonical interface: `notebooks/thesis_empirical_pipeline.ipynb`.
Canonical outputs: `results/final/`.

## Pipeline Steps

1. Rebuild processed EU/DE data - completed with exit code 0.
2. Rebuild ECB external instrument pipeline - completed with exit code 0.
3. Run canonical baseline LP-IV - completed with exit code 0.
4. Run weak-IV robustification layer - completed with exit code 0.
5. Run final empirical audit - completed with exit code 0.

## Empirical Visibility

- Baseline response-horizon cells: 30.
- First-stage F-statistic range: 0.0157 to 0.2434.
- First-stage weak-IV flags: {'weak_iv_risk': 30}.
- Weak-IV classification counts: {'directional_only': 30}.
- Top ranked directional channels: NFC credit, Housing, HH credit.

Magnitude inference remains weak-IV constrained. The final interpretation is directional and persistence-based.
