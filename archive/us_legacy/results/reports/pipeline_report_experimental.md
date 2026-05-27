# Thesis VECM Pipeline Report

Status: COMPLETED_EXPERIMENTAL_WITH_DIAGNOSTIC_WARNINGS
Experimental override: True

## Gatekeeping Messages

- Stationarity gate failed. Non-I(1) classifications: shadow_rate=difference-stationary/ambiguous; ln_real_housing=unclear; ln_cpi=unclear.
- Lag selection used HQIC and selected k_ar_diff=2.
- Cointegration gate passed with rank 2 of 6.
- Adjustment gate passed. 8 alpha coefficients are significant at 5%.
- Diagnostics gate warning: autocorrelation in ['ln_real_housing', 'ln_real_income']; ARCH effects in ['ln_real_equity', 'ln_real_income', 'ln_cpi']
- Proxy IRFs generated with the local Fed JK monetary policy shock file.

Selected short-run lag order: 2

Selected cointegration rank: 2

## Research Interpretation

The current local files reproduce the old U.S./Fed-oriented workflow. They are useful for code validation and audit, but they do not satisfy the thesis requirement for a Germany-first ECB/Bundesbank/Eurostat data system.

A thesis-grade run should replace this legacy dataset with Germany/Euro Area series before accepting VECM estimates or impulse responses as evidence for the thesis.
