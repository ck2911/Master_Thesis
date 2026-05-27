# Thesis VECM Pipeline Report

Status: STOPPED_BY_STATIONARITY_GATE
Experimental override: False

## Gatekeeping Messages

- Stationarity gate failed. Non-I(1) classifications: shadow_rate=difference-stationary/ambiguous; ln_real_housing=unclear; ln_cpi=unclear.

## Research Interpretation

The current local files reproduce the old U.S./Fed-oriented workflow. They are useful for code validation and audit, but they do not satisfy the thesis requirement for a Germany-first ECB/Bundesbank/Eurostat data system.

A thesis-grade run should replace this legacy dataset with Germany/Euro Area series before accepting VECM estimates or impulse responses as evidence for the thesis.
