# Main_Files Extraction Notes

`Main_Files/` was treated as a legacy instruction archive and retired from the live project structure. The current project no longer imports code or data from that folder.

## What Was Learned From The Old Notebooks

- The intended empirical architecture was a monthly macro-financial VECM, not a pure SVAR.
- The economic blocks were: monetary policy, financial intermediation, asset prices, income, and inflation.
- The working sample was approximately 2005 onward, with a COVID split around March 2020.
- The notebooks experimented with ADF/KPSS stationarity checks, Johansen rank testing, VECM estimation, and proxy-VECM impulse responses.
- The external-instrument logic used Jarocinski-Karadi style Fed monetary policy shocks, which is useful as a coding prototype but not valid for the final Germany/ECB thesis question.

## Important Code-Level Findings

- `draft_3.ipynb` used the intended U.S. Case-Shiller housing price index (`CSUSHPINSA`).
- `draft_4.ipynb` accidentally defined `Housing` twice in `series_dict`, so the intended housing-price series was overwritten by U.S. housing starts (`HOUST`).
- The old notebooks used a hardcoded FRED API key and runtime network calls, which is not reproducible thesis infrastructure.
- Lag selection was computed but then not consistently used in the fitted VECM.
- Cointegration rank was tested but then hardcoded in estimation.
- Stationarity results were not treated as a binding gate, even when some variables were not defensibly I(1).
- Pre/post-COVID subsample models were estimated without rechecking stationarity, lag order, rank, sample adequacy, or diagnostics.
- IRF confidence bands were not implemented in a thesis-defensible way.

## What Was Preserved

- Root-level `1. SSR_estimates_M.xlsx` is now the live legacy policy-rate/shadow-rate source.
- Root-level `6. shocks_fed_jk_m.csv` is now the live legacy shock source.
- Extracted aligned legacy macro data were saved under `data/legacy_us/`.
- The audit and methodology lessons were preserved in `docs/`.

## What Was Discarded

The `Main_Files/` folder itself was discarded because it was a source of stale notebooks, duplicate files, hidden path assumptions, and methodological ambiguity.

