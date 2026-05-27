# LP-IV Identification Strategy

Date: 2026-05-15

This document records the frozen LP-IV identification strategy. It is not a new instrument search memo.

## Frozen Baseline Decision

Official baseline instrument:

- `target_factor_market_magnitude_weighted_quarterly_sum`

Endogenous policy variable:

- `d_ecb_assets_ea_qavg`

The LP-IV system treats the selected instrument as imperfect but usable for infrastructure validation. The choice follows prior first-stage screening, regime diagnostics, information-effect screening, aggregation robustness, weighted-shock analysis, and feasibility assessment. The implementation does not reopen instrument selection.

## Identification Equation

For each response variable and horizon:

```text
y_{t+h} - y_{t-1} = alpha_h + beta_h * policy_hat_t + Gamma_h X_t + epsilon_{t+h}
```

The first stage instruments `d_ecb_assets_ea_qavg` with the frozen target-factor weighted shock and the same horizon-specific control set used in the second stage.

## Why LP-IV Replaces Proxy-SVECM

The project does not abandon identification. It changes the estimation architecture because the transmission mechanism appears regime-dependent and structurally unstable. A proxy-SVECM would force a more globally stable dynamic system than the diagnostics support. LP-IV lets the project test horizon responses and regime interactions without rebuilding a globally stable VAR framework.

## Imperfect Strength Handling

The instrument is accepted as the official baseline because it is the best thesis-aligned candidate after the closed diagnostic phase. The LP-IV implementation still reports:

- horizon-specific first-stage F-statistics,
- partial R2,
- rolling coefficient stability,
- regime-specific relevance,
- regime and quarter contribution shares.

These diagnostics are required before any response interpretation. Weakness or concentration warnings are validation evidence, not automatic thesis conclusions.

## DAX Treatment

`ln_dax_real_de` is robustness-only. It is excluded from baseline beta logic because the baseline asks whether liquidity transmission propagates into bank intermediation, housing wealth, and real compensation. DAX is useful for checking broader asset-price inflation, but including it in the baseline would blur the credit-vs-real-income channel contrast and increase exposure to market information effects.
