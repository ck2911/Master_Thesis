# Final Reduced-Form Specification

Date: 2026-05-16

## Canonical Estimand

The empirical object is the dynamic response to a high-frequency ECB monetary-policy surprise aggregated to month. The canonical shock is `target_factor_monthly_easing`; timing, forward-guidance, QE, and weighted-composite surprises are robustness factors.

## Local Projection

```text
y_{t+h} - y_{t-1}
  = alpha_h + beta_h * surprise_t
    + phi_1 y_{t-1} + phi_2 y_{t-2}
    + gamma_1 inflation_{t-1} + gamma_2 inflation_{t-2}
    + delta_1 dfr_{t-1} + delta_2 dfr_{t-2}
    + epsilon_{t+h}
```

Horizon grid: `0, 1, 3, 6, 12, 24` months. Inference uses HAC/Newey-West covariance with horizon-specific bandwidth `h + 1`. The specification is not tuned by response variable.

## Normalization

CSV column `coefficient` is the response to a one-standard-deviation surprise shock. `raw_coefficient_per_unit_shock` preserves the unscaled regression coefficient. `coefficient_10bp_equiv` is provided as an optional basis-point interpretation, conditional on treating factor units as basis points.

## Cumulative Responses

Cumulative tables sum normalized horizon coefficients. Cumulative confidence intervals use an independence approximation for the summed standard errors and are interpreted as descriptive transmission persistence, not exact structural cumulative multipliers.

## Uncertainty Communication

Each IRF row reports HAC/Newey-West confidence intervals with horizon-specific bandwidth `h + 1`; 68%, 90%, and 95% bands are retained in the CSV contract. Full-sample target-shock IRFs also report feasible circular-block residual percentile bootstrap intervals. The final uncertainty folder additionally reports moving-block, wild, block-length sensitivity, and horizon-dependence diagnostics. Significance heatmaps and persistence-confidence matrices are communication devices for uncertainty, not new causal estimands.

## Regime Decomposition

Regime estimates are split into pre-QE, QE, COVID, and tightening windows using `lp_monthly_regime`. They are descriptive heterogeneous-transmission evidence. They are not clean regime treatment effects.

## Governance

No quarterly housing or compensation series is interpolated. Housing-price and compensation-per-employee constructs enter the monthly comparison only through accepted real monthly proxies documented in `docs/proxy_validation.md`.
