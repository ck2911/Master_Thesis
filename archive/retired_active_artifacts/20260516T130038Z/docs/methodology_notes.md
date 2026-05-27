# Methodology Notes

## Research Question

The thesis studies whether post-COVID ECB monetary expansion transmitted primarily through productive credit channels or through financial and asset-price channels, with special attention to Germany-facing outcomes.

The empirical mechanism is:

```text
ECB policy shock -> credit allocation -> asset prices vs real purchasing power
```

## Selected Econometric Architecture

The final architecture is a **Structural VECM (SVECM) with external monetary instruments**.

The maintained logic is:

- The endogenous macro-financial variables are persistent and potentially cointegrated.
- Differencing everything would discard long-run balance-sheet, credit, and asset-price information.
- A reduced-form VECM preserves equilibrium structure.
- External monetary instruments will identify structural ECB policy innovations.

The current phase prepares the system; it does not estimate the final identified SVECM.

## Permanent Samples

- Baseline sample: 2005Q1-2022Q2, using `wx_shadow_rate`.
- Robustness sample: 2005Q1-2025Q4, using `dfr_eop`.

All active code should inherit these windows from `config/sample_windows.json` or `src/svecm/specification.py`.

## Current Endogenous Block

Core block:

- `ln_ecb_assets_ea_stock`
- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`

Expanded financial-asset block:

- core block plus `ln_dax_real_de`

## Policy And Identification Block

Policy variables should not be forced into the long-run cointegration vector. The baseline policy variable is `wx_shadow_rate`; the robustness policy variable is `dfr_eop`.

The final identification layer will require a validated ECB monetary-surprise instrument. The current repository includes schema and alignment infrastructure for that future instrument in `src/svecm/external_instruments.py`.

## Diagnostic Gates

Before final estimation, the project must pass:

1. File and transformation audit.
2. Stationarity diagnostics for all endogenous candidates.
3. Johansen rank sensitivity across deterministic assumptions and lag lengths.
4. Structural-break controls for 2008, 2012, 2015, 2020, and 2022.
5. External-instrument relevance and validity checks.
6. Residual diagnostics and stability checks after the final SVECM is estimated.
