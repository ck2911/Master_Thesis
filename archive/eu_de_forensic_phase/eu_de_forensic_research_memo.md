# Euro Area / Germany Forensic Data Assessment Memo

Date: 2026-05-15  
Workspace: `/Users/ck/Documents/New project/THESIS_Model`  
Data folder: `/Users/ck/Documents/New project/THESIS_Model/data/EU:DE`

## 1. Executive Recommendation

The downloaded Euro Area / Germany dataset is useful, but it is not yet a clean one-for-one replacement for the earlier U.S. VECM system. The strongest current evidence supports a **quarterly hybrid framework**:

1. **Main long-run model:** a parsimonious quarterly VECM using I(1)-type level variables for credit, housing assets, purchasing power, and optionally equity assets.
2. **Policy and lending standards:** treated as exogenous, shock, or short-run mechanism variables rather than forced into the cointegration space.
3. **Retail trade:** used only in stationary growth-rate robustness work, not as a level variable.
4. **ECB balance sheet:** excluded from the current core model because the downloaded file is annual year-end data. A monthly or weekly ECB total-assets / APP / PEPP stock series should be downloaded before any final QE-balance-sheet inference.

Recommended current core endogenous VECM set:

- `ln_hh_loans_ea_stock`: Euro Area adjusted household loan stock.
- `ln_nfc_loans_ea_stock`: Euro Area adjusted NFC loan stock.
- `ln_house_price_de_real`: German residential property prices deflated by German HICP.
- `ln_compensation_ea20_real`: Euro Area 20 compensation per employee deflated by EA20 HICP.
- `ln_dax_real_de`: real DAX close, included in the expanded core if explicit financial-asset inflation is required.

Recommended policy/shock variable:

- Use **Wu-Xia Euro Area shadow rate** as the primary monetary stance proxy for the 2005Q1-2022Q2 shadow-rate sample.
- Use **ECB Deposit Facility Rate** only as a robustness/full-sample conventional-rate alternative.
- Do **not** include both in the same baseline system.

The strongest Johansen evidence is for **rank 1** in the real credit-housing-income block, and rank 1 remains plausible when real DAX is added. However, cointegrating vectors are not fully stable across pre-COVID and full samples, so the final model should include break dummies/pulses and should avoid overfitting lag length.

## 2. Files Inspected And Structure Findings

### 1. Wu-Xia Euro Area Shadow Rate.xls

- Format: legacy `.xls`, one sheet, 216 rows x 2 columns.
- Structure: no metadata rows, no column headers. Column 1 is `YYYYMM`; column 2 is the shadow-rate value.
- Frequency: monthly.
- Sample: 2004-09 to 2022-08; quarterly aggregation produces a partial 2022Q3 value.
- Unit: percent policy/shadow-rate level.
- Transformation status: raw level, not differenced or annualized.
- Cleaning: convert `YYYYMM` to month-end dates; use quarterly average for quarterly model.
- Suitability: conceptually central as ECB stance; statistically bounded/rate-like and should not be forced into the long-run cointegration vector.
- Risk: ends before the full 2022-2025 hiking/normalization period.

### 2. Annual_consolidated_balance_sheet_Eurosystem.xls

- Format: legacy `.xls`, one sheet, 52 rows x 28 columns.
- Structure: rows 1-5 are title/unit/header metadata; assets begin at row 6; `Total assets` is row 27; liabilities begin row 28; `Total liabilities` is row 50.
- Frequency: annual year-end.
- Sample: 1999-2025.
- Unit: EUR millions.
- Useful extracted measures: `ecb_total_assets`; `ecb_monetary_policy_securities`.
- Transformation status: raw annual stock levels.
- Suitability: not suitable for the quarterly/monthly VECM from the current file because it has only 27 annual observations.
- Risk: total assets and monetary-policy securities are almost duplicate long-run trends; annual correlation is 0.973. Total assets also correlate strongly with real house prices, so it would dominate a small system if interpolated.
- Recommendation: exclude from the final model until a monthly or weekly ECB balance-sheet stock is obtained.

### 3. ECB Deposit Facility Rate.xlsx

- Format: `.xlsx`, README sheet plus `Daily, 7-Day` sheet.
- Structure: FRED metadata in README; daily observations with `observation_date` and `ECBDFR`.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: daily, converted to monthly/quarterly averages and end-of-period rates.
- Sample: 2005-01-01 to 2025-12-31.
- Unit: percent, not seasonally adjusted.
- Transformation status: raw policy-rate level, piecewise constant.
- Suitability: useful as robustness or full-sample conventional-rate proxy, but weak during ZLB/negative-rate period.
- Redundancy: monthly common-sample correlation with Wu-Xia shadow rate is 0.837; end-of-period and average DFR correlate 0.998.
- Recommendation: do not include with Wu-Xia in the same baseline.

### 4. Loans To Euro Area Households Granted By MFIs.xlsx

- Format: `.xlsx`, one `DATA` sheet, 294 rows x 3 columns.
- Structure: ECB metadata rows 1-14; data header row 15; observations begin row 16.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: monthly.
- Sample: 2003-01 to 2026-03.
- Unit: EUR millions.
- Geography: Euro Area changing composition.
- Transformation status: adjusted loan stock, end-of-period level; not a growth rate.
- Suitability: central variable for household/housing/asset-channel transmission.
- Risk: log-level stationarity diagnostics are ambiguous because of breaks and persistence, but the series is economically a stock and should be treated as near-I(1) for cointegration testing.

### 5. Adjusted Loans To Euro Area NFCs Granted By MFIs.xlsx

- Format: `.xlsx`, one `DATA` sheet, 294 rows x 3 columns.
- Structure: ECB metadata rows 1-14; data header row 15; observations begin row 16.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: monthly.
- Sample: 2003-01 to 2026-03.
- Unit: EUR millions.
- Geography: Euro Area changing composition.
- Transformation status: adjusted NFC loan stock, end-of-period level; not a growth rate.
- Suitability: essential productive-credit variable.
- Risk: highly persistent and structurally affected by crisis/COVID lending programs. Household and NFC loan log levels correlate 0.927, so do not add an aggregate credit series on top of both.

### 6. Credit Standards - Enterprise

- Format: `.xlsx`, one `DATA` sheet, 109 rows x 3 columns.
- Structure: ECB metadata rows 1-14; data header row 15; observations begin row 16.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: quarterly, beginning-of-period survey timing converted to quarter-end.
- Sample: 2003Q1 to 2026Q2.
- Unit: percent net tightening.
- Transformation status: diffusion/survey balance, already stationary-like and bounded.
- Suitability: useful as mechanism evidence or exogenous short-run supply condition for firm lending.
- Recommendation: do not include as an endogenous VECM level variable.

### 6.1 Credit Standards - Household

- Format: `.xlsx`, one `DATA` sheet, 109 rows x 3 columns.
- Structure: same ECB metadata/data layout as enterprise standards.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: quarterly.
- Sample: 2003Q1 to 2026Q2.
- Unit: percent net tightening.
- Transformation status: diffusion/survey balance.
- Suitability: useful as auxiliary evidence for the household/housing channel.
- Evidence: household credit standards have negative lead correlations with future real house-price growth, around -0.34 at 1-2 quarter leads.
- Recommendation: use as exogenous/auxiliary, not as a cointegrating level.

### 7. Residential Prices.xlsx

- Format: `.xlsx`, FRED README plus `Quarterly` sheet.
- Structure: README metadata; data sheet has `observation_date` and `QDEN628BIS`.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: quarterly.
- Sample: 2005Q1 to 2025Q4.
- Unit: Germany residential property price index, 2010=100.
- Seasonal adjustment: not seasonally adjusted.
- Transformation status: nominal index level.
- Cleaning: convert quarter-start FRED dates to quarter-end; construct real house prices using German HICP.
- Suitability: central asset-price variable; real log level is I(1) by preferred tests.
- Risk: strong structural breaks around 2020 and 2022; may dominate IRFs if not scaled and modeled carefully.

### 8. DAX 40.csv

- Format: CSV with `Date`, `Open`, `High`, `Low`, `Close`, `Volume`.
- Frequency: monthly, month-end.
- Sample: 2005-01 to 2026-01.
- Unit: index level and volume.
- Source metadata: absent from file.
- Cleaning: use close; deflate by German HICP for real DAX.
- Suitability: plausible financial-asset-price proxy, but volatile and less tightly anchored to bank lending than housing.
- Recommendation: include in expanded core or robustness; drop before credit/housing/income if the model becomes unstable.

### 9. Compensation Per Employee.xlsx

- Format: `.xlsx`, one `DATA` sheet, 139 rows x 3 columns.
- Structure: ECB metadata rows 1-14; data header row 15; observations begin row 16.
- Hidden/merged issues: no hidden rows/columns; no merged cells.
- Frequency: quarterly.
- Sample: 1995Q1 to 2025Q4.
- Unit: nominal index.
- Geography: Euro Area 20 fixed composition, not Germany.
- Transformation status: nominal index level, average through period.
- Cleaning: construct real compensation using EA20 HICP.
- Suitability: central purchasing-power proxy, but geography mismatch must be disclosed.
- Risk: severe COVID compensation shock; real compensation has a 2020Q2 event z-score of -8.25 versus pre-2020 growth behavior.

### 10. Volume Of Sales In Wholesale And Retail Trade.xlsx

- Format: `.xlsx`, Summary sheet plus `Sheet 1`.
- Structure: Eurostat metadata rows 1-9; date headers at row 10; geography/category rows 12-23; Germany retail trade row is row 20.
- Hidden/merged issues: no hidden rows/columns. The data sheet has 253 merged month header ranges, and freeze panes at `C12`.
- Frequency: monthly.
- Unit: percentage change on previous period.
- Seasonal adjustment: seasonally and calendar adjusted.
- Geography: Germany.
- Transformation status: already transformed growth rate, not a raw volume index.
- Cleaning: extract Germany / retail trade except motor vehicles; preserve the official MoM percent change; construct a chained index only for visualization.
- Suitability: `retail_de_mom_pct` is stationary and appropriate for VAR/robustness, not VECM long-run levels. The chained index should not be treated as an official level series.

### 11. HICP - Monthly Data.tsv

- Format: wide Eurostat TSV.
- Structure: first column is a compound key `freq,unit,coicop,geo\TIME_PERIOD`; columns are monthly periods.
- Frequency: monthly.
- Sample: generally 1996-01 to 2025-12; EA20 starts later.
- Unit: index 2015=100.
- Extracted rows: `M,I05,CP00,DE`, `M,I05,CP00,EA20`, and `M,I05,CP00,EA`.
- Transformation status: price-level index.
- Suitability: best used as deflator for real house prices, real compensation, real DAX, and possibly real credit sensitivity checks.
- Risk: do not include HICP as an endogenous level at the same time as real-transformed variables unless intentionally estimating a nominal price-level block.

## 3. Cleaning And Standardization Decisions

- Dates were standardized to month-end or quarter-end.
- Monthly stocks were aggregated to quarterly using end-of-quarter values.
- Daily DFR was aggregated using both quarterly average and end-of-quarter values.
- Monthly HICP was converted to quarterly averages for real transformations.
- Retail trade was kept as MoM percent growth; a chained index normalized to 2005-01=100 was produced only as a diagnostic convenience.
- Real variables were constructed as:
  - `house_price_de_real = house_price_de / hicp_de * 100`
  - `compensation_ea20_real = compensation_ea20_nominal / hicp_ea20 * 100`
  - `dax_real_de = dax_close / hicp_de * 100`

Primary cleaned files:

- `results/eu_de_forensic/tables/eu_de_monthly_clean.csv`
- `results/eu_de_forensic/tables/eu_de_quarterly_clean.csv`
- `results/eu_de_forensic/tables/eurosystem_balance_sheet_annual_clean.csv`
- `results/eu_de_forensic/tables/eu_de_variable_metadata.csv`

## 4. Stationarity Diagnostics Summary

Preferred quarterly-level classifications:

| Variable | Preferred transform | Classification | Interpretation |
|---|---:|---|---|
| `wx_shadow_rate` | level | I(1) by tests | Economically bounded policy variable; use as shock/exogenous, not cointegration level. |
| `dfr_eop` | level | difference-stationary/ambiguous | Piecewise constant policy rate; robustness only. |
| `hh_loans_ea_stock` | log | unclear / near-I(1) | Persistent stock with breaks; retain because theory-central. |
| `nfc_loans_ea_stock` | log | unclear / near-I(1) | Persistent stock with breaks; retain because theory-central. |
| `credit_standards_enterprise` | level | I(0) | Exogenous/auxiliary mechanism variable. |
| `credit_standards_household` | level | I(0) | Exogenous/auxiliary mechanism variable. |
| `house_price_de_real` | log | I(1) | Strong candidate for VECM. |
| `compensation_ea20_real` | log | I(1) | Strong candidate, with geography caveat. |
| `dax_real_de` | log | I(1) | Expanded core or robustness. |
| `retail_de_mom_pct` | level | I(0) | Stationary demand-growth proxy, not VECM level. |
| `retail_de_chained_index` | log | I(1) | Constructed level; not robust enough for final model. |
| `hicp_de` | log | near-I(1)/ambiguous | Use mainly as deflator or nominal-price robustness. |
| `ecb_total_assets` | log | I(1) | Annual only; exclude from high-frequency model. |

Zivot-Andrews break-unit-root tests generally did **not** reject unit roots in the major log-level variables even allowing one break, reinforcing the case for a VECM rather than mechanically differenced VAR for the core stock/asset/income variables.

## 5. Structural Break Assessment

Important break evidence:

- DFR shows significant trend breaks at 2008, 2012, 2020, and 2022.
- Wu-Xia shadow rate shows significant breaks at 2008 and 2020.
- Household and NFC loan stocks show strong trend breaks at 2008 and 2012.
- Real German house prices show significant trend breaks at 2008, 2012, 2020, and 2022.
- Real DAX shows significant breaks at 2008, 2012, and 2022.
- Real compensation shows a strong 2022 trend break and an extreme COVID shock in 2020Q2.

Event z-score highlights versus pre-2020 behavior:

- `compensation_ea20_real`, 2020Q2: -8.25.
- `hicp_de`, 2022Q3: +3.34.
- `house_price_de_real`, 2022Q3: -3.04.
- `credit_standards_household`, 2022Q3: +3.19.
- `wx_shadow_rate`, 2022Q3 partial quarter: +3.00.

The final model should include at minimum COVID and 2022 inflation/tightening break controls. A clean thesis-grade system should also test 2008 and 2012 crisis dummies.

## 6. Cointegration Findings

Johansen rank sensitivity was run on several quarterly candidate systems.

### Core real credit-housing-income system

Variables:

- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`

Full sample: 2005Q1-2025Q4, 84 observations.  
Finding: rank 1 is the most defensible baseline across constant/no-trend specifications and lags 1-2. Some trend specifications and longer lags become unstable, which argues against overfitting.

### Core plus real DAX

Variables:

- Core real system above
- `ln_dax_real_de`

Finding: rank 1 remains plausible and relatively stable under det_order 0 at lags 1-2. DAX beta coefficients are small in the first cointegrating vector, suggesting it adds financial-asset information but is a weaker long-run anchor than credit, housing, and compensation.

### Nominal price-level system

Variables:

- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de`
- `ln_compensation_ea20_nominal`
- `ln_hicp_de`

Finding: rank is less stable, often 1-2 and sometimes implausibly high pre-COVID. This system risks confusing nominal price-level cointegration with the thesis mechanism.

### Systems including policy rates

Adding `wx_shadow_rate` or `dfr_eop` directly into the Johansen system raises rank and full-rank artifacts. This is consistent with mixing bounded/rate-like variables with I(1) stock variables. Policy variables should be exogenous, used for shocks, or used in short-run equations, not forced into beta.

## 7. Frequency Compatibility

Quarterly harmonization is preferable:

- Residential prices are quarterly.
- Compensation is quarterly.
- Credit standards are quarterly.
- Loans, DFR, DAX, and HICP can be safely aggregated to quarterly.
- Retail is monthly but already a stationary growth rate; quarterly averages are fine for robustness.
- The current balance-sheet file is annual and should not be interpolated into quarterly data for the final model.

Monthly VECM would require interpolating house prices and compensation, which would create artificial persistence. Annual VECM would throw away almost all useful variation and leave too few observations.

## 8. Variable Inclusion Recommendations

### Include In Main Or Expanded Core

- `hh_loans_ea_stock`: central household/asset-channel credit stock.
- `nfc_loans_ea_stock`: central productive-credit stock.
- `house_price_de_real`: central housing asset-price variable.
- `compensation_ea20_real`: best available purchasing-power proxy, with geography caveat.
- `dax_real_de`: include if the final model must explicitly identify financial asset inflation; otherwise use as robustness.
- `wx_shadow_rate`: monetary stance/shock variable for 2005Q1-2022Q2, not beta.

### Use As Robustness / Auxiliary Mechanism Evidence

- `dfr_eop` or `dfr_avg`: alternative conventional policy proxy, not with Wu-Xia.
- `credit_standards_enterprise`: short-run firm credit supply mechanism.
- `credit_standards_household`: short-run household/mortgage credit supply mechanism.
- `retail_de_mom_pct`: stationary household-demand robustness variable.
- `hicp_de` and `hicp_ea20`: deflators; possible nominal-price robustness variables.
- `dax_real_de`: robustness if omitted from the main core.

### Exclude From Current Final Core

- `ecb_total_assets`: exclude because current file is annual only.
- `ecb_monetary_policy_securities`: same annual-frequency problem; also redundant with total assets.
- `retail_de_chained_index`: constructed from percentage changes, not an official downloaded level.
- `retail_de_mom_pct`: exclude from VECM levels because it is already stationary growth.
- Simultaneous `wx_shadow_rate` and `dfr_eop`: redundant and identification-weak.
- Simultaneous real variables and their deflator as if they are independent long-run variables, unless a nominal block is intentionally specified.

## 9. Econometric Risks

- **Geography mismatch:** policy and loans are Euro Area; house prices and DAX are Germany; compensation is EA20. This is acceptable for a Germany-centered ECB transmission thesis only if framed explicitly as ECB/EA financial conditions transmitted into German asset and purchasing-power outcomes.
- **Balance-sheet proxy missing:** the annual balance-sheet file is not enough for final QE inference.
- **High persistence and breaks:** loan stocks, HPI, DAX, compensation, and HICP all contain major crisis/COVID/inflation breaks.
- **Collinearity:** household and NFC loans have 0.927 log-level correlation; household loans and HICP also exceed 0.90; real house prices and the constructed retail index correlate 0.949.
- **Policy-rate redundancy:** Wu-Xia and DFR are highly correlated where both exist, while DFR loses informational content under the ZLB/negative-rate regime.
- **Survey variables are I(0):** useful mechanism variables, but inappropriate in the cointegrating vector.
- **DAX source quality:** the CSV lacks source metadata and does not include dividends; use cautiously.
- **Retail file is not a volume index:** it is a percentage-change file; do not treat the chained reconstruction as official.
- **Sample length:** quarterly full sample has about 84 observations for the key system; this does not support a large VECM.

## 10. Final Recommended Econometric Framework

Baseline:

- Quarterly VECM, rank 1, parsimonious lag length.
- Endogenous I(1) block:
  - `ln_hh_loans_ea_stock`
  - `ln_nfc_loans_ea_stock`
  - `ln_house_price_de_real`
  - `ln_compensation_ea20_real`
  - optionally `ln_dax_real_de`
- Policy variable:
  - `wx_shadow_rate` as exogenous/shock or ordered policy variable for the shadow-rate sample.
- Deterministic controls:
  - constant in cointegration relation; test no-trend and restricted-trend alternatives.
- Break controls:
  - 2008 financial crisis
  - 2012 euro crisis
  - 2020Q2 COVID pulse
  - 2022 inflation/tightening shock

Robustness:

- Replace Wu-Xia with DFR for full 2005-2025 sample.
- Add credit standards as exogenous short-run controls.
- Estimate a stationary VAR or local projection using:
  - changes in policy rate/shadow rate
  - credit growth
  - real DAX returns
  - real house-price growth
  - retail MoM/quarterly growth
  - credit-standard levels

Data improvement required before final thesis model:

- Download a **monthly or weekly ECB total assets / APP / PEPP / monetary-policy securities stock series**. The annual balance-sheet workbook should remain descriptive only.

