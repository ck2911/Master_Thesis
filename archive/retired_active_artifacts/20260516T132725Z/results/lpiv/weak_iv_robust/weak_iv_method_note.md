# Weak-IV Robustification Method Note

This validation layer preserves the frozen baseline LP-IV specification.

Anderson-Rubin tests are implemented by testing beta0 in:

`y_{t+h} - y_{t-1} - beta0 * d_ecb_assets_ea_qavg_t`

on the frozen external instrument and frozen two-lag controls, using the same Newey-West bandwidth rule as the baseline LP-IV.

The reported AR p-value tests `beta0 = 0`. The AR confidence interval is a grid inversion of the 10 percent AR test. Unbounded intervals are reported as `-inf` or `inf` and interpreted as weak-IV inconclusive.

Cell classification:

- `robust_signal`: AR rejects zero and the inverted AR interval is bounded and excludes zero
- `directional_only`: AR is inconclusive, but the sign is stable across controlled comparison layers
- `unidentified`: neither weak-IV robust rejection nor directional stability is present

Regime AR diagnostics are reported only where feasible. Short regime subsamples, especially COVID and baseline-window tightening, are flagged as not feasible rather than forced into false precision.
