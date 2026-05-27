# Final Sample-Window Documentation

## Baseline Sample

- Window: 2005Q1-2022Q2
- Date range: 2005-03-31 to 2022-06-30
- Policy variable: `wx_shadow_rate`
- Reason: aligns with Wu-Xia Euro Area shadow-rate coverage and captures the GFC, euro crisis, QE, ZLB/negative-rate period, and COVID/PEPP liquidity expansion without using the partial 2022Q3 shadow-rate endpoint.

## Robustness Sample

- Window: 2005Q1-2025Q4
- Date range: 2005-03-31 to 2025-12-31
- Policy variable: `dfr_eop`
- Reason: preserves the full post-2022 hiking and normalization period using the conventional ECB Deposit Facility Rate.

## Implementation

The canonical dataset includes:

- `baseline_sample`
- `robustness_sample`

Future scripts should trim by these flags or use `src/svecm/specification.py`.
