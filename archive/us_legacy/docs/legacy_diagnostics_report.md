# Diagnostics Report

## Strict Run

The strict pipeline stopped at the stationarity gate.

Failed variables:

- `shadow_rate`: difference-stationary/ambiguous
- `ln_real_housing`: unclear
- `ln_cpi`: unclear

This means the current local system should not be used as a thesis-grade VECM.

## Experimental Legacy Run

The experimental override was run only to verify the later code path.

- Selected short-run lag order: `k_ar_diff = 2` by HQIC.
- Selected cointegration rank: `rank = 2` by Johansen trace test.
- Significant adjustment coefficients: 8 alpha coefficients at the 5 percent level.
- First stage using the local Fed shock file: F-statistic approximately 10.98, p-value approximately 0.0011, R-squared approximately 0.047.

Residual diagnostics still reject a clean model:

- Autocorrelation warning: `ln_real_housing`, `ln_real_income`
- ARCH warning: `ln_real_equity`, `ln_real_income`, `ln_cpi`
- Strong non-normality appears across several residual equations.

## Research Interpretation

The legacy system is useful for validating the modular code, but its estimates should not be used as thesis evidence. The diagnostics imply that even as a U.S. exercise, the model would need further specification work before making substantive claims.

