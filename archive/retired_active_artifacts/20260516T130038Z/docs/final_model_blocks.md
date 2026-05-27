# Final Recommended Model Blocks

## Endogenous Core Block

Recommended for the main quarterly SVECM:

- `ln_ecb_assets_ea_stock`
- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`

## Expanded Endogenous Block

Recommended robustness/expanded financial-asset block:

- core block
- `ln_dax_real_de`

## Baseline Exogenous / Shock Block

Baseline sample: 2005Q1-2022Q2.

- `wx_shadow_rate`
- `credit_standards_enterprise`
- `credit_standards_household`
- `dummy_gfc_2008q4`
- `dummy_euro_crisis_2012q3`
- `dummy_qe_launch_2015q1`
- `dummy_covid_2020q2`

The future external monetary instrument should enter the identification layer, not the beta vector.

## Robustness Exogenous / Shock Block

Robustness sample: 2005Q1-2025Q4.

- `dfr_eop`
- `credit_standards_enterprise`
- `credit_standards_household`
- `dummy_gfc_2008q4`
- `dummy_euro_crisis_2012q3`
- `dummy_qe_launch_2015q1`
- `dummy_covid_2020q2`
- `dummy_2022_tightening_q3`

## Rank Guidance

Preliminary diagnostics with the new ECB assets variable support a cointegrated system. Rank 1 is the conservative starting point, while rank 2 should be tested because the baseline core block often selects trace rank 2 and max-eigen rank 1.

No final SVECM has been estimated in this phase.
