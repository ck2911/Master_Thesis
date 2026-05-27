# Weak Exogeneity Report

Scope: pre-identification stress testing only. These tests do not estimate the final SVECM.

## Alpha Restriction Tests

Null hypothesis: `alpha_i = 0`. Rejection means the candidate adjusts to the long-run relation and is not weakly exogenous under the tested system/rank.

| sample | system | candidate | nobs | rank_selected_trace | rank_tested | lr_stat | df | p_value | decision_5pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | System A: ECB assets inside beta | ln_ecb_assets_ea_stock | 70.000 | 2.000 | 2.000 | 7.217 | 2.000 | 0.027 | reject alpha_i = 0 |
| robustness | System A: ECB assets inside beta | ln_ecb_assets_ea_stock | 84.000 | 1.000 | 1.000 | 10.672 | 1.000 | 0.001 | reject alpha_i = 0 |
| baseline | Policy extension: Wu-Xia in beta candidate | wx_shadow_rate | 70.000 | 2.000 | 2.000 | 1.230 | 2.000 | 0.541 | fail to reject alpha_i = 0 |
| robustness | Policy extension: DFR in beta candidate | dfr_eop | 84.000 | 2.000 | 2.000 | 25.039 | 2.000 | 0.000 | reject alpha_i = 0 |
| baseline | Expanded: DAX in beta candidate | ln_dax_real_de | 70.000 | 1.000 | 1.000 | 0.912 | 1.000 | 0.339 | fail to reject alpha_i = 0 |
| robustness | Expanded: DAX in beta candidate | ln_dax_real_de | 84.000 | 1.000 | 1.000 | 0.193 | 1.000 | 0.660 | fail to reject alpha_i = 0 |

## System Rank Comparison

Default comparison uses a restricted constant in the cointegrating relation (`ecdet = const`) and VAR lag `K = 2`.

| sample | system | nobs | trace_rank_5pct | maxeig_rank_5pct | trace_r0_stat | trace_r0_cv5 | stability_comment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | System A: ECB assets inside beta | 70.000 | 2.000 | 1.000 | 143.002 | 76.070 | trace/max-eigen disagreement |
| robustness | System A: ECB assets inside beta | 84.000 | 1.000 | 1.000 | 123.313 | 76.070 | trace and max-eigen agree |
| baseline | System B: ECB assets outside beta block | 70.000 | 2.000 | 2.000 | 121.531 | 53.120 | trace and max-eigen agree |
| robustness | System B: ECB assets outside beta block | 84.000 | 1.000 | 1.000 | 96.013 | 53.120 | trace and max-eigen agree |
| baseline | System C: DAX excluded | 70.000 | 2.000 | 1.000 | 143.002 | 76.070 | trace/max-eigen disagreement |
| robustness | System C: DAX excluded | 84.000 | 1.000 | 1.000 | 123.313 | 76.070 | trace and max-eigen agree |
| baseline | System D: ECB assets excluded | 70.000 | 2.000 | 2.000 | 121.531 | 53.120 | trace and max-eigen agree |
| robustness | System D: ECB assets excluded | 84.000 | 1.000 | 1.000 | 96.013 | 53.120 | trace and max-eigen agree |
| baseline | Expanded: ECB assets plus DAX | 70.000 | 1.000 | 1.000 | 164.564 | 102.140 | trace and max-eigen agree |
| robustness | Expanded: ECB assets plus DAX | 84.000 | 1.000 | 1.000 | 152.637 | 102.140 | trace and max-eigen agree |

## Beta Interpretation

The first unrestricted Johansen beta vector is normalized on the first listed variable. Large opposite-signed coefficients are a warning sign in this trend-dominated system, not a final structural restriction.

| system | sample | normalized_on | variable | beta_first_vector |
| --- | --- | --- | --- | --- |
| System A: ECB assets inside beta | baseline | ln_ecb_assets_ea_stock | ln_ecb_assets_ea_stock | 1.000 |
| System A: ECB assets inside beta | baseline | ln_ecb_assets_ea_stock | ln_hh_loans_ea_stock | 182.926 |
| System A: ECB assets inside beta | baseline | ln_ecb_assets_ea_stock | ln_nfc_loans_ea_stock | -30.633 |
| System A: ECB assets inside beta | baseline | ln_ecb_assets_ea_stock | ln_house_price_de_real | -70.770 |
| System A: ECB assets inside beta | baseline | ln_ecb_assets_ea_stock | ln_compensation_ea20_real | -421.493 |
| System B/D: ECB assets excluded beta block | baseline | ln_hh_loans_ea_stock | ln_hh_loans_ea_stock | 1.000 |
| System B/D: ECB assets excluded beta block | baseline | ln_hh_loans_ea_stock | ln_nfc_loans_ea_stock | -0.124 |
| System B/D: ECB assets excluded beta block | baseline | ln_hh_loans_ea_stock | ln_house_price_de_real | -0.393 |
| System B/D: ECB assets excluded beta block | baseline | ln_hh_loans_ea_stock | ln_compensation_ea20_real | -2.311 |
| Expanded: ECB assets plus DAX | baseline | ln_ecb_assets_ea_stock | ln_ecb_assets_ea_stock | 1.000 |
| Expanded: ECB assets plus DAX | baseline | ln_ecb_assets_ea_stock | ln_hh_loans_ea_stock | -831.561 |
| Expanded: ECB assets plus DAX | baseline | ln_ecb_assets_ea_stock | ln_nfc_loans_ea_stock | 136.051 |
| Expanded: ECB assets plus DAX | baseline | ln_ecb_assets_ea_stock | ln_house_price_de_real | 290.519 |
| Expanded: ECB assets plus DAX | baseline | ln_ecb_assets_ea_stock | ln_compensation_ea20_real | 1919.606 |
| Expanded: ECB assets plus DAX | baseline | ln_ecb_assets_ea_stock | ln_dax_real_de | 4.240 |

## Economic Interpretation

- ECB assets should only remain inside beta if alpha and beta stability both support an endogenous liquidity equilibrium. A failure to reject `alpha_i = 0` for ECB assets supports treating liquidity as a forcing process; rejection supports endogenous adjustment but must be weighed against collinearity.
- `wx_shadow_rate` and `dfr_eop` are policy-side stance variables. If their alpha restrictions fail to reject, they should stay outside beta and enter short-run or instrument-side identification.
- DAX is structurally useful only if it contributes stable rank information without worsening near-singularity. Weak exogeneity alone is not sufficient because DAX is a high-volatility asset-price robustness variable.

Supporting CSV outputs: `weak_exogeneity_alpha_tests.csv`, `weak_exogeneity_rank_sensitivity.csv`, and `weak_exogeneity_beta_vectors.csv`.
