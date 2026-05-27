# EU/DE Restructuring Report

Date: 2026-05-15

## Target Architecture Implemented

The repository now follows the Euro Area / Germany research structure:

```text
data/
  raw/eu_de/
  processed/eu_de/
  archive/
notebooks/
  data_engineering/
  diagnostics/
  vecm/
  svecm/
  robustness/
src/
  data/
  transformations/
  diagnostics/
  cointegration/
  svecm/
  irf/
  plotting/
results/
  diagnostics/
  stationarity/
  cointegration/
  svecm/
  irf/
  robustness/
archive/
  retired_prototypes/
```

## Active Pipeline Entrypoint

```text
scripts/run_eu_de_consolidation.sh
```

This builds the canonical dataset and reruns ECB asset diagnostics.

## Canonical Dataset

```text
data/processed/eu_de/final_quarterly_model_dataset.csv
```

The dataset is quarterly, spans 2005Q1-2025Q4, and contains sample flags for the baseline and robustness windows.

## Configuration Files

- `config/sample_windows.json`
- `config/model_blocks.json`
- `config/structural_breaks.csv`

These files are now the stable interface for future SVECM estimation scripts.
