# Final Estimation Protocol

This document is the canonical empirical contract for the baseline LP-IV estimation phase. It freezes the specification used to estimate ECB liquidity transmission dynamics through credit, housing, and compensation responses.

The objective is disciplined structural response evidence. This protocol does not reopen identification, instrument selection, model architecture, or the variable set.

## 1. Identification Structure

The baseline design is an external-instrument local projection IV model. The endogenous policy variable is:

`d_ecb_assets_ea_qavg`

The baseline instrument is:

`target_factor_market_magnitude_weighted_quarterly_sum`

The estimator is horizon-by-horizon two-stage least squares.

For each response variable `y` and horizon `h`, the local projection outcome is:

`y_{t+h} - y_{t-1}`

The first stage projects the endogenous policy variable on the external instrument and the frozen lagged controls:

`d_ecb_assets_ea_qavg_t = pi_h z_t + Gamma_h controls_{t-1:t-2} + u_t`

The second stage projects the horizon-specific response on the fitted policy component and the same controls:

`y_{t+h} - y_{t-1} = beta_h fitted_policy_t + B_h controls_{t-1:t-2} + e_{t+h}`

The structural IRF at horizon `h` is `beta_h`.

## 2. Data Contracts

Baseline LP-IV estimation may read only:

`data/processed/eu_de/final_quarterly_model_dataset.csv`

`data/processed/eu_de/ecb_surprise_quarterly.csv`

No other active data source is permitted for baseline LP-IV estimation.

The baseline sample is:

`2005Q1` through `2022Q2`

The robustness sample, when explicitly activated outside the baseline, is:

`2005Q1` through `2025Q4`

## 3. Frozen Baseline Variables

Baseline responses are:

`ln_ecb_assets_ea_stock`

`ln_hh_loans_ea_stock`

`ln_nfc_loans_ea_stock`

`ln_house_price_de_real`

`ln_compensation_ea20_real`

The frozen baseline horizon set is:

`0, 1, 2, 4, 8, 12`

DAX is excluded from the baseline and may enter only as a robustness block.

## 4. Horizon Construction

The official LP dependent-variable structure is:

`y_{t+h} - y_{t-1}`

This is the only permitted baseline horizon transformation.

The baseline explicitly prohibits:

- cumulative rolling growth windows as the regression outcome
- ad hoc response transformations
- overlapping custom horizon windows outside the frozen horizon set
- unrestricted SVAR or unrestricted proxy-SVECM response construction

Cumulative IRFs are constructed after estimation by summing the estimated IRF coefficients over the frozen reported horizon grid up to horizon `h`.

## 5. Lag Structure and Deterministic Components

The baseline includes two lags of the frozen control vector:

- `ln_ecb_assets_ea_stock`
- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`
- `inflation_ea20_qoq`
- `wx_shadow_rate`

The deterministic component is an intercept in both stages. No linear trend is included in the canonical baseline.

## 6. HAC Inference

Inference uses Newey-West HAC covariance estimation.

Bandwidth is horizon-dependent:

`bandwidth_h = max(1, h + 1)`

Confidence bands are reported at:

- 68 percent
- 90 percent

Coefficient tables also retain p-values and t-statistics from the HAC standard errors.

## 7. Baseline Instrument Definition

The baseline instrument is the quarterly sum of target-factor surprises after market-magnitude weighting:

`target_factor_market_magnitude_weighted_quarterly_sum`

Aggregation logic:

- event-level target-factor monetary surprises are assigned to their event quarter
- event surprises within a quarter are summed
- the quarterly value preserves the signed direction of the weighted surprise

Weighting logic:

- event-level target-factor surprises are scaled by market-magnitude weights before quarterly aggregation
- the intent is to emphasize events with larger market-information content while retaining the target-factor interpretation

Event-to-quarter transformation:

- all eligible ECB monetary-surprise events in a quarter are mapped to that quarter
- quarters with multiple events accumulate the weighted event contributions
- quarters without qualifying events contribute no active surprise signal

Caveats:

- instrument variation is crisis-concentrated and must be diagnosed explicitly
- regime sensitivity is expected because event density and market reactions are not uniform across monetary-policy regimes
- weak-horizon interpretation rules apply whenever first-stage relevance deteriorates

## 8. Weak-IV Interpretation Protocol

Every horizon-specific structural estimate must be interpreted together with its horizon-specific first-stage relevance.

| F-stat | Interpretation |
|---:|---|
| > 10 | strong |
| 5 to 10 | moderate caution |
| < 5 | weak-IV risk |

Horizon masking and annotation rules:

- `F_stat < 5`: flag as `weak_iv_risk`; figures must visibly mark the estimate as weak-IV sensitive
- `5 <= F_stat < 10`: flag as `moderate_caution`; figures must annotate the estimate as relevance-limited
- `F_stat > 10`: flag as `strong`

Interpretation restrictions:

- no strong causal language at weak-IV-risk horizons
- no narrative extrapolation from unstable long-horizon tails
- weak horizons may be described directionally only, and only with explicit caution
- persistence claims require both same-sign estimates and relevance diagnostics

## 9. Regime Architecture

Regime definitions are frozen as:

| Regime | Start | End |
|---|---:|---:|
| pre-QE | 2005Q1 | 2014Q1 |
| QE | 2014Q2 | 2019Q4 |
| COVID | 2020Q1 | 2021Q4 |
| tightening | 2022Q1 | 2025Q4 |

In the baseline sample, the tightening regime is observed only through `2022Q2`. Full tightening-regime evidence belongs to robustness analysis and must not contaminate the baseline interpretation.

## 10. Interpretation Scope

Allowed interpretation:

- directional macro transmission
- relative strength across credit, housing, and compensation channels
- timing and persistence differences
- regime dependence when relevance permits

Prohibited interpretation:

- welfare claims
- inequality claims
- household affordability causal claims
- broad political conclusions
- policy prescriptions
- FEVDs, historical decompositions, or counterfactual paths
