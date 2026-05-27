# LP-IV Diagnostics Framework

Date: 2026-05-15

Diagnostics are a required gate before interpreting any impulse response. The current phase is infrastructure validation only.

## Required Diagnostics

Residual diagnostics:

- residual autocorrelation,
- Breusch-Pagan-style heteroskedasticity statistic,
- leverage,
- standardized residual outliers,
- Cook's-distance-style influence screen.

First-stage diagnostics:

- F-statistics,
- partial R2,
- rolling relevance,
- regime-specific relevance,
- residual plots,
- horizon-specific relevance.

Stability diagnostics:

- rolling LP-IV coefficients,
- regime contribution shares,
- quarter contribution shares.

## Output Paths

The diagnostics layer writes to:

- `results/lpiv/diagnostics/`
- `results/lpiv/diagnostics/first_stage/`

Key files include:

- `baseline_residual_diagnostics.csv`
- `baseline_horizon_first_stage_quality.csv`
- `baseline_rolling_lpiv_coefficients.csv`
- `baseline_regime_contribution.csv`
- `baseline_quarter_contribution.csv`
- `first_stage/baseline_first_stage.csv`
- `first_stage/rolling_first_stage.csv`
- `first_stage/regime_first_stage.csv`

## Reading Rule

Diagnostics can identify weak horizons, regime concentration, influential quarters, or residual instability. They do not by themselves establish welfare claims, policy effectiveness, or final causal conclusions. Their role is to validate whether the LP-IV response estimates are usable for later thesis interpretation.
