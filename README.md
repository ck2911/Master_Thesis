# ECB Monetary Surprise Transmission

This repository supports a thesis on post-COVID ECB monetary transmission in the Euro Area and Germany. The study asks whether expansionary ECB policy-news shocks transmit more strongly through housing-credit and selected financial-intermediation channels than through compensation-linked real-economy variables.

The empirical design uses high-frequency ECB announcement surprises as external policy-news shocks. The responses are estimated with a local-projection / SVAR-style response logic: identify the shock outside the monthly macro data, then trace impulse responses across housing credit, lending conditions, credit aggregates, financial markets, and compensation-linked variables.

The core question is:

```text
Did post-COVID ECB monetary easing transmit more strongly through housing-credit
and financial-intermediation channels than through compensation-linked
real-economy variables?
```

## Repository Structure

- `1. thesis_master_notebook.ipynb`: main empirical notebook for reading the results; it lives at the repository root so it sorts to the top in file browsers.
- `src/data/`: construction of monthly and quarterly research datasets.
- `src/lpiv/`: local-projection and external-instrument estimation tools.
- `scripts/`: rebuild scripts for shocks, proxy selection, estimation, figures, and tables.
- `LATEX/`: thesis writing and XeLaTeX compilation workspace.
- `results/final/`: figures, tables, uncertainty checks, and mechanism outputs used by the thesis.
- `docs/`: short research notes on identification, findings, and interpretation boundaries.

## Main Findings

House-purchase lending growth is the clearest and most persistent response. Lending spreads and other intermediation variables support a housing-credit transmission interpretation.

Financial-market responses are mixed. In particular, the negative real DAX response should be read through an information-effects lens: ECB announcements may combine policy accommodation with adverse macroeconomic information.

Compensation-linked and wage-pressure proxies respond less consistently than the housing-credit block. This does not mean income-side variables never move; it means they do not show the same durable response profile as house-purchase credit growth and lending conditions.

## Methodology

The monetary shock is built from high-frequency ECB surprise measures and signed so that positive values correspond to easing surprises. The main response estimates use monthly impulse responses with HAC and bootstrap uncertainty.

The design keeps quarterly house-price and compensation-per-employee series at their observed frequency. Monthly comparisons rely on observed monthly proxies, especially house-purchase lending growth, pure-new mortgage-flow checks, lending spreads, and negotiated-wage-pressure series.

Robustness checks use alternative ECB surprise factors, clean-event samples, regime splits, rolling estimates, recursive estimates, COVID exclusions, and alternative wage and housing-credit proxies.

## Interpretation Boundary

The repository supports reduced-form evidence of heterogeneous monetary transmission. It does not identify household welfare effects, inequality, redistribution, exact house-price effects, or structural bank mediation.

## Running The Results

From the repository root:

```bash
python scripts/run_full_pipeline.py
```

The main notebook is:

```text
1. thesis_master_notebook.ipynb
```

The notebook is the canonical reading interface. The old `notebooks/` folder is no longer used for the active thesis notebook.
