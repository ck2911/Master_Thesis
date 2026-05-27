# draft_4.ipynb Audit

This audit summarizes the existing notebook before the rebuild.

## What Exists

- Data are assembled at monthly frequency from U.S.-centric sources.
- The estimated system is a VECM with a policy rate/shadow rate, bank credit, equity prices, housing, income, and CPI transformations.
- The notebook runs ADF and KPSS checks, Johansen rank testing, VECM estimation, basic plotting, and external-instrument impulse responses using Jarocinski-Karadi style Fed shocks.
- The proposal is SVAR-based, while the notebook has moved toward VECM because several macro-financial variables appear nonstationary and cointegrated.

## Salvageable Elements

- Monthly frequency alignment is appropriate for the available macro-financial series.
- The VECM turn is methodologically sensible if the final variables are I(1) and cointegrated.
- The high-level variable blocks are close to the thesis architecture: monetary policy, intermediation, asset prices, real income, and inflation.
- The external-instrument idea remains useful, but it must be changed to an ECB/Euro Area monetary policy surprise series for a Germany-first thesis.

## Major Problems

- The empirical system is U.S./Fed-focused, not Germany/ECB-focused.
- The notebook contains a hardcoded FRED API key and depends on runtime network calls.
- The `series_dict` defines `Housing` twice; the second entry overwrites the Case-Shiller house price index with U.S. housing starts.
- The VECM includes a policy-rate variable even though the notebook's own stationarity table classifies it as I(0), which conflicts with a strict I(1) cointegration system.
- Johansen testing suggests a higher rank than the hardcoded rank used in estimation.
- Lag selection is computed but not consistently used.
- Missing-value handling is performed after `dropna`, so the median imputation step is redundant and conceptually misleading.
- Some IRF comparison code labels the housing response as income because of an index-position error.
- The IRF confidence-band calculation can produce invalid square roots and is not a defensible bootstrap inference procedure.
- Pre/post-COVID subsample VECMs are estimated without checking sample size, lag order, stationarity, rank, or diagnostics for each subsample.
- There are no residual diagnostics, stability checks, or structural-break screens sufficient for thesis-grade inference.

## Research Consequence

The current notebook should not be interpreted as evidence for the German post-COVID monetary transmission thesis. It is best treated as an exploratory prototype whose architecture can be reused after replacing the data with Germany/Euro Area official series and applying strict VECM gatekeeping.

