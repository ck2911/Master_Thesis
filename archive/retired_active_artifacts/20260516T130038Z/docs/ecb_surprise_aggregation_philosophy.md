# ECB Surprise Event-to-Quarter Aggregation Philosophy

Date: 2026-05-15

This note documents the pre-estimation aggregation rule for the EU/DE External-Instrument LP-IV system. It is deliberately upstream of response interpretation.

## Baseline Rule

The canonical baseline aggregation is `quarterly_sum` of the ABGMR `timing` factor.

The reason is theoretical: high-frequency ECB surprises are flow/news shocks. If more than one Governing Council event occurs in a quarter, the quarterly economy receives multiple pieces of monetary-policy information. Summing preserves that cumulative information arrival, while averaging would shrink quarters with several events merely because the ECB met more often.

## Robustness Rules

The pipeline also exports three robustness transformations for every factor:

- `quarterly_mean`: scale robustness that checks whether results depend on meeting-count intensity.
- `absolute_sum`: intensity-only robustness that ignores the easing/tightening sign and measures shock magnitude.
- `signed_cumulative`: final within-quarter cumulative signed surprise after sorting events by date. At a quarterly endpoint this equals the signed quarterly sum, but it is exported separately to make the cumulative-news interpretation auditable.

## Baseline and Robustness Roles

The baseline external instrument is:

```text
timing_factor_quarterly_sum
```

The `target_factor`, `fg_factor`, and `qe_factor` series are preserved for robustness, decomposition, and transmission diagnostics. They are not intended to enter the baseline LP-IV simultaneously.

The lightweight Jarocinski-Karadi-style screen uses signs of `OIS_6M` and `STOXX50` from the EA-MPD monetary-event window. It is an interpretation layer only, not a replacement for the baseline instrument.
