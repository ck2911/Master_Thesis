# LP-IV Inference Design

Date: 2026-05-15

The inference layer is implemented in `src/lpiv/inference.py` without relying on statsmodels. It uses pandas and numpy so the LP-IV pipeline can run in the current project runtime.

## Estimator

The baseline estimator is two-stage least squares:

1. Project `d_ecb_assets_ea_qavg` on the frozen external instrument and controls.
2. Estimate each horizon response on the instrumented policy variable and controls.

The same controls enter the first and second stages.

## Horizon Outcomes

For every response and horizon, the outcome is:

```text
y_{t+h} - y_{t-1}
```

This is a Jordà-style future change. It is not a rolling cumulative window and not an ad hoc overlapping growth rate.

Baseline horizons are `0, 1, 2, 4, 8, 12`. The robustness specification also includes horizon `16`.

## HAC Standard Errors

All reported standard errors use Newey-West HAC covariance. The default bandwidth is horizon-dependent:

```text
bandwidth_h = max(1, h + 1)
```

Confidence bands are reported at:

- 68 percent,
- 90 percent,
- 95 percent.

Bands use asymptotic normal critical values. Naive OLS standard errors are not used for reported LP-IV inference.

## Controls

Control lags are configured through `LPIVSpecification.control_lags`. The default is two lags of:

- ECB assets,
- household loans,
- NFC loans,
- real German house prices,
- real EA20 compensation,
- EA20 inflation,
- the selected policy-rate control.

The lag count is not hardcoded globally.
