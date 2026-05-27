# Beta Stability Testing

Rolling Johansen diagnostics were estimated over the robustness sample using 40-, 48-, and 56-quarter windows. The default specification uses `ecdet = const` and VAR lag `K = 2`.

## Rank Frequencies

| system | window | rank_trace_5pct | count | share |
| --- | --- | --- | --- | --- |
| core_with_ecb_assets | 40 | 1 | 1.000 | 0.022 |
| credit_housing_income_no_ecb | 48 | 1 | 2.000 | 0.054 |
| core_with_ecb_assets | 56 | 1 | 5.000 | 0.172 |
| credit_housing_income_no_ecb | 56 | 1 | 5.000 | 0.172 |
| core_with_ecb_assets | 40 | 2 | 8.000 | 0.178 |
| credit_housing_income_no_ecb | 40 | 2 | 13.000 | 0.289 |
| core_with_ecb_assets | 48 | 2 | 16.000 | 0.432 |
| credit_housing_income_no_ecb | 48 | 2 | 16.000 | 0.432 |
| core_with_ecb_assets | 56 | 2 | 21.000 | 0.724 |
| credit_housing_income_no_ecb | 56 | 2 | 17.000 | 0.586 |
| core_with_ecb_assets | 40 | 3 | 16.000 | 0.356 |
| credit_housing_income_no_ecb | 40 | 3 | 15.000 | 0.333 |
| core_with_ecb_assets | 48 | 3 | 10.000 | 0.270 |
| credit_housing_income_no_ecb | 48 | 3 | 12.000 | 0.324 |
| core_with_ecb_assets | 56 | 3 | 3.000 | 0.103 |
| credit_housing_income_no_ecb | 56 | 3 | 7.000 | 0.241 |
| core_with_ecb_assets | 40 | 4 | 9.000 | 0.200 |
| credit_housing_income_no_ecb | 40 | 4 | 17.000 | 0.378 |
| core_with_ecb_assets | 48 | 4 | 6.000 | 0.162 |
| credit_housing_income_no_ecb | 48 | 4 | 7.000 | 0.189 |
| core_with_ecb_assets | 40 | 5 | 11.000 | 0.244 |
| core_with_ecb_assets | 48 | 5 | 5.000 | 0.135 |

## Regime Summary

| system | window | regime | rank_trace_5pct |
| --- | --- | --- | --- |
| core_with_ecb_assets | 40.000 | COVID 2020-2021 | median=5; mode=5; n=8 |
| credit_housing_income_no_ecb | 40.000 | COVID 2020-2021 | median=4; mode=4; n=8 |
| core_with_ecb_assets | 48.000 | COVID 2020-2021 | median=4.5; mode=4; n=8 |
| credit_housing_income_no_ecb | 48.000 | COVID 2020-2021 | median=4; mode=4; n=8 |
| core_with_ecb_assets | 56.000 | COVID 2020-2021 | median=2; mode=2; n=8 |
| credit_housing_income_no_ecb | 56.000 | COVID 2020-2021 | median=3; mode=3; n=8 |
| core_with_ecb_assets | 40.000 | Pre-QE 2005-2014 | median=3; mode=3; n=1 |
| credit_housing_income_no_ecb | 40.000 | Pre-QE 2005-2014 | median=2; mode=2; n=1 |
| core_with_ecb_assets | 40.000 | QE era 2015-2019 | median=3.5; mode=3; n=20 |
| credit_housing_income_no_ecb | 40.000 | QE era 2015-2019 | median=3; mode=3; n=20 |
| core_with_ecb_assets | 48.000 | QE era 2015-2019 | median=3; mode=2; n=13 |
| credit_housing_income_no_ecb | 48.000 | QE era 2015-2019 | median=3; mode=3; n=13 |
| core_with_ecb_assets | 56.000 | QE era 2015-2019 | median=2; mode=2; n=5 |
| credit_housing_income_no_ecb | 56.000 | QE era 2015-2019 | median=2; mode=2; n=5 |
| core_with_ecb_assets | 40.000 | Tightening 2022-2025 | median=3; mode=3; n=16 |
| credit_housing_income_no_ecb | 40.000 | Tightening 2022-2025 | median=2.5; mode=2; n=16 |
| core_with_ecb_assets | 48.000 | Tightening 2022-2025 | median=2; mode=2; n=16 |
| credit_housing_income_no_ecb | 48.000 | Tightening 2022-2025 | median=2; mode=2; n=16 |
| core_with_ecb_assets | 56.000 | Tightening 2022-2025 | median=2; mode=2; n=16 |
| credit_housing_income_no_ecb | 56.000 | Tightening 2022-2025 | median=2; mode=2; n=16 |

Generated plots: `eigenvalue_evolution_plots.png` and `beta_coefficient_drift_plots.png`.
