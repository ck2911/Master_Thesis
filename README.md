# ECB Monetary Surprise Transmission

This repository supports a thesis on post-COVID monetary transmission in the euro area and Germany. The study asks whether expansionary ECB policy surprises move mainly through asset prices, housing finance, and lending conditions, or whether they pass through with similar strength into wages and real household income.

The empirical design uses high-frequency ECB announcement surprises as external monetary shocks. The responses are estimated with an SVAR/local-projection response logic: identify the policy-news shock outside the monthly macro data, then trace impulse responses across financial, housing, credit, and compensation variables.

The core question is simple:

Do expansionary monetary-policy surprises transmit primarily into financial assets and housing finance, or into real household income and compensation?

## Repository Structure

- `notebooks/`: main empirical notebook for reading the results.
- `src/data/`: construction of monthly and quarterly research datasets.
- `src/lpiv/`: local-projection and external-instrument estimation tools.
- `scripts/`: rebuild scripts for shocks, proxy selection, estimation, figures, and tables.
- `results/final/`: figures, tables, uncertainty checks, and mechanism outputs used by the thesis.
- `docs/`: short research notes on identification, findings, and interpretation boundaries.

## Main Findings

Housing and financial variables respond more strongly and more persistently than compensation variables. The clearest evidence appears in housing-finance growth, lending spreads, and other financial-intermediation measures.

Compensation and wage-pressure proxies respond more weakly and less consistently. This does not mean wages never move. It means the wage and compensation block does not show the same durable response as housing finance and lending conditions.

The main thesis result is therefore asymmetric transmission: expansionary ECB surprises appear to work more through financial and housing channels than through broad real-income pass-through.

## Methodology

The monetary shock is built from high-frequency ECB surprise measures and signed so that positive values correspond to easing surprises. The main response estimates use monthly impulse responses with HAC and bootstrap uncertainty.

The design keeps quarterly house-price and compensation-per-employee series at their observed frequency. Monthly comparisons rely on observed monthly proxies, especially housing-finance measures and negotiated-wage-pressure series.

Robustness checks use alternative ECB surprise factors, clean-event samples, regime splits, rolling estimates, recursive estimates, COVID exclusions, and alternative wage and housing-finance proxies.

## Running The Results

From the repository root:

```bash
python scripts/run_full_pipeline.py
```

The main notebook is:

```text
notebooks/thesis_empirical_pipeline.ipynb
```
