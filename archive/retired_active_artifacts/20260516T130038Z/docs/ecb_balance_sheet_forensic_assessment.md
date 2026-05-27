# ECB Balance-Sheet Forensic Assessment

Date: 2026-05-15  
File: `data/raw/eu_de/ecb_central_bank_assets_weekly.csv`

## File Structure

- Workbook sheets: `README`, `Weekly`.
- `README` row 8 identifies the series as `ECBASSETSW`.
- Full description: Central Bank Assets for Euro Area (11-19 Countries), Millions of Euros, Weekly, Not Seasonally Adjusted.
- Data sheet: 1,095 weekly observations plus header.
- Columns: `observation_date`, `ECBASSETSW`.
- Hidden formatting: no hidden rows, hidden columns, merged ranges, or freeze panes.

## Coverage And Units

- Frequency: weekly.
- Sample in raw file: 2005-01-07 to 2025-12-26.
- Unit: millions of euros.
- Seasonal adjustment: not seasonally adjusted.
- Transformation status: raw stock level.
- Economic coverage: Euro Area central-bank assets, not APP-only or PEPP-only. It is broad Eurosystem/central-bank balance-sheet liquidity, appropriate as a general liquidity/QE stock proxy.

## Quarterly Construction

The canonical pipeline constructs:

- `ecb_assets_ea_stock`: end-of-quarter weekly stock.
- `ecb_assets_ea_qavg`: quarterly average weekly stock.
- `ecb_assets_ea_trillions`: end-of-quarter stock divided by 1,000,000.
- `ln_ecb_assets_ea_stock`: natural log of the end-of-quarter stock.

The final SVECM liquidity variable should be `ln_ecb_assets_ea_stock`.

## Statistical Diagnostics

Stationarity diagnostics classify `ln_ecb_assets_ea_stock` as I(1):

- ADF level p-value: 0.473.
- KPSS level p-value: 0.010.
- ADF first-difference p-value: 0.0046.
- KPSS first-difference p-value: 0.100.

This is exactly the persistence profile expected for a balance-sheet stock variable in a VECM/SVECM.

## Structural Breaks

Chow-style trend-break screens on log ECB assets:

- 2008Q4: significant, p = 0.043.
- 2012Q3: significant, p = 0.002.
- 2015Q1: not significant in this simple trend-break screen, p = 0.325.
- 2020Q2: strongly significant, p < 0.001.
- 2022Q3: strongly significant, p < 0.001.

Event growth z-scores versus pre-2020 behavior:

- 2008Q4 quarterly log growth: z = 3.61.
- 2020Q2 quarterly log growth: z = 2.43.
- 2022Q3 quarterly log growth: z = -0.41, but the trend-break test captures the post-2022 runoff regime.

## Cointegration Diagnostics

Adding the ECB asset stock strengthens the case for a cointegrated quarterly system.

Baseline sample, 2005Q1-2022Q2:

- Core liquidity-credit-housing-income block generally selects rank 2 by trace and rank 1 by max-eigen across common specifications.
- Expanded block with real DAX generally selects rank 1-2 depending on deterministic terms.

Robustness sample, 2005Q1-2025Q4:

- Core block usually selects rank 1.
- Expanded block with real DAX usually selects rank 1, with occasional rank 2 under trend specifications.

Interpretation: the new liquidity variable is suitable for the long-run SVECM block, but final rank selection should remain conservative and test rank 1 vs rank 2.

## Liquidity Channel Evidence

Baseline level correlations with log ECB assets are high:

- Real house prices: 0.867.
- Real DAX: 0.777.
- Real compensation: 0.847.
- Household loans: 0.943.
- NFC loans: 0.605.

Four-quarter growth correlations are more discriminating:

- Real house prices: 0.257.
- Real DAX: -0.286.
- Real compensation: -0.083.
- Household loans: 0.224.
- NFC loans: 0.333.

The evidence supports a stronger link between balance-sheet expansion and housing/credit dynamics than real compensation growth. It does not support using DAX as the sole asset-inflation proxy; DAX remains useful as an expanded financial-asset robustness variable.

## Recommendation

The new file is suitable as the **primary liquidity / QE variable** for the final quarterly SVECM.

Use:

```text
ln_ecb_assets_ea_stock
```

Keep:

```text
ecb_assets_ea_qavg
```

as a robustness liquidity construction.
