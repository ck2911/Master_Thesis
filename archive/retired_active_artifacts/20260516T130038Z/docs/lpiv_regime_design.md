# LP-IV Regime Design

Date: 2026-05-15

Regime flexibility is central to the LP-IV architecture. The implementation does not assume a single stable transmission coefficient across the full sample.

## Regime Windows

The LP-IV regime indicators are:

| Regime | Window |
| --- | --- |
| `pre_qe` | 2005Q1 to 2014Q1 |
| `qe` | 2014Q2 to 2019Q4 |
| `covid` | 2020Q1 to 2021Q4 |
| `tightening` | 2022Q1 to 2025Q4 |

These windows are generated in `src/lpiv/specifications.py` and attached to the merged LP-IV dataset as explicit dummy variables.

## Interaction Estimator

The regime estimator instruments policy-by-regime terms with instrument-by-regime terms:

```text
d_ecb_assets_ea_qavg x regime_r
```

instrumented by:

```text
target_factor_market_magnitude_weighted_quarterly_sum x regime_r
```

The output is stored under `results/lpiv/regime/`.

## Purpose

The regime layer measures whether the same ECB liquidity shock has different horizon responses across monetary-policy eras. This is a validation design, not a policy narrative. Small-regime estimates must be interpreted through first-stage and contribution diagnostics before any substantive claim is made.
