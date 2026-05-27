# SVECM Architecture Preparation Memo

Date: 2026-05-15

## Architecture Decision

The project has formally moved to:

```text
Structural VECM with external monetary instruments
```

This preserves long-run cointegration while allowing structural ECB monetary shocks to be identified outside a recursive unrestricted SVAR.

## Implemented Code Infrastructure

### Data

- `src/data/build_final_dataset.R`
  - Parses heterogeneous raw files.
  - Standardizes date indexes.
  - Aggregates to quarterly frequency.
  - Constructs real variables and logs.
  - Writes the canonical quarterly dataset.

### Diagnostics

- `src/diagnostics/stationarity.py`
  - ADF, KPSS, and Phillips-Perron wrappers.
- `src/diagnostics/ecb_assets_assessment.py`
  - ECB asset visual diagnostics.
  - Stationarity tests.
  - Structural-break screens.
  - Liquidity-channel correlations.
  - Johansen rank diagnostics involving ECB assets.

### Cointegration

- `src/cointegration/johansen.py`
  - Lag-selection and rank-sensitivity helpers.

### SVECM Specification

- `src/svecm/specification.py`
  - Permanent sample windows.
  - Endogenous and exogenous block definitions.
  - Design-matrix loader that refuses missing canonical variables.

### External Instruments

- `src/svecm/external_instruments.py`
  - Future ECB monetary-surprise loader.
  - Residual/instrument alignment.
  - First-stage relevance table.
  - Proxy impact-vector normalization.

### IRFs

- `src/irf/svecm_irf.py`
  - Structural IRF table helper for a future fitted VECM and proxy impact vector.

## What Is Deliberately Not Implemented Yet

- Final SVECM estimation.
- Final external-instrument selection.
- Final structural shock recovery.
- Final structural IRF interpretation.

Those steps should occur only after the final monetary-surprise instrument is selected and validated.

## Next Implementation Step

Select and ingest an ECB monetary-surprise instrument, then run instrument relevance and validity diagnostics before estimating the identified SVECM.
