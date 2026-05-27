# Final Transformation Documentation

## Canonical Builder

The final dataset is built by:

```text
src/data/build_final_dataset.R
```

Run through:

```text
scripts/run_eu_de_consolidation.sh
```

## Date Convention

All observations are standardized to quarter-end dates.

- Monthly stock series: end-of-quarter value.
- Daily policy rate: end-of-quarter and quarterly average.
- Weekly ECB assets: end-of-quarter stock and quarterly average.
- Quarterly series: converted to quarter-end.
- Monthly HICP: quarterly average.
- Monthly retail growth: quarterly average.

## Real Transformations

Real variables are constructed as:

```text
house_price_de_real = house_price_de / hicp_de * 100
compensation_ea20_real = compensation_ea20_nominal / hicp_ea20 * 100
dax_real_de = dax_close / hicp_de * 100
```

## Log Transformations

Positive stock/index variables are transformed with natural logs. The final core log variables are:

- `ln_ecb_assets_ea_stock`
- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`
- `ln_dax_real_de`

## Policy Variables

- `wx_shadow_rate`: quarterly average of monthly Wu-Xia Euro Area shadow rate.
- `dfr_eop`: end-of-quarter ECB Deposit Facility Rate.
- `dfr_qavg`: quarterly average ECB Deposit Facility Rate.

Policy variables are not part of the long-run cointegrating vector in the recommended architecture.

## Liquidity Variable

- `ecb_assets_ea_stock`: end-of-quarter weekly central-bank assets, EUR millions.
- `ln_ecb_assets_ea_stock`: final primary liquidity/QE variable.

## Auxiliary Variables

- `credit_standards_enterprise`
- `credit_standards_household`
- `retail_de_mom_pct_qavg`
- crisis and regime dummies

Credit standards and retail growth are not long-run endogenous level variables.
