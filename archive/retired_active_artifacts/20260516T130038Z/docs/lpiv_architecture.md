# LP-IV Architecture

Date: 2026-05-15

This phase builds the External-Instrument Local Projection infrastructure for the Euro Area / Germany monetary-transmission thesis. It does not estimate a final SVECM, write thesis conclusions, run FEVDs, run historical decompositions, run counterfactuals, or make policy recommendations.

## Methodological Pivot

The project has pivoted from a proxy-SVECM baseline to LP-IV because prior diagnostics showed regime sensitivity, unstable transmission, weak timing instruments, episodic QE dominance, and non-constant first-stage relevance. The SVECM code remains available only as archived robustness infrastructure. The active architecture must not impose a globally stable VAR transmission system.

LP-IV is now preferred because each response horizon can be estimated directly while preserving flexible sample, regime, and diagnostic checks. This is aligned with the working thesis question: whether ECB liquidity shocks transmit differently across regimes and whether transmission moves more through productive intermediation or asset-price inflation.

## Active Data Contract

The LP-IV layer consumes only:

- `data/processed/eu_de/final_quarterly_model_dataset.csv`
- `data/processed/eu_de/ecb_surprise_quarterly.csv`

The quarterly surprise file is now the self-contained LP-IV external-instrument table. Weighted, bridge, and composite surprise variants can be generated upstream, but LP-IV estimation code does not read those side files as active modeling inputs.

## Module Map

- `src/lpiv/specifications.py`: sample windows, response sets, official instrument, controls, regimes, and robustness specifications.
- `src/lpiv/horizon_design.py`: Jordà outcomes `y_{t+h} - y_{t-1}` and configurable lag-control construction.
- `src/lpiv/inference.py`: numpy/pandas 2SLS and Newey-West HAC covariance.
- `src/lpiv/first_stage.py`: first-stage relevance, rolling relevance, regime relevance, and residual plots.
- `src/lpiv/local_projection_iv.py`: response-horizon LP-IV runner and table output.
- `src/lpiv/regime_interactions.py`: shock-by-regime LP-IV estimators.
- `src/lpiv/diagnostics.py`: residual, rolling, horizon relevance, and contribution diagnostics.
- `src/lpiv/plotting.py`: SVG IRF and residual plotting utilities.

## Output Contract

Generated outputs live under:

- `results/lpiv/baseline/`
- `results/lpiv/robustness/`
- `results/lpiv/regime/`
- `results/lpiv/diagnostics/`
- `results/lpiv/diagnostics/first_stage/`
- `results/lpiv/plots/` with specification subdirectories such as `baseline/` and `robustness/`
- `results/lpiv/tables/`

Tables are written as CSV, with XLSX where the local runtime supports it. Markdown summaries are validation notes only.

## Baseline Scope

Baseline responses are:

- `ln_ecb_assets_ea_stock`
- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`

`ln_dax_real_de` is excluded from baseline beta logic because it is a high-frequency financial-asset robustness object rather than part of the core liquidity-credit-housing-income transmission block. DAX remains available as robustness-only evidence for asset-price amplification.
