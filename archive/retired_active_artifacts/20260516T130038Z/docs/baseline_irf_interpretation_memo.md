# Baseline IRF Interpretation Memo

This memo records disciplined baseline LP-IV interpretation only. It is not final thesis prose and does not make welfare, inequality, affordability, or policy-prescription claims.

## Governing Weak-IV Caveat

All canonical baseline horizons are weak-IV-risk horizons under the frozen protocol.

The horizon-specific first-stage F-statistics are:

| Horizon | F-stat | Flag |
|---:|---:|---|
| 0 | 0.206 | weak-IV risk |
| 1 | 0.220 | weak-IV risk |
| 2 | 0.243 | weak-IV risk |
| 4 | 0.166 | weak-IV risk |
| 8 | 0.047 | weak-IV risk |
| 12 | 0.016 | weak-IV risk |

Therefore, the baseline IRFs can be read only as relevance-limited structural response patterns. They cannot support strong causal magnitudes, strong persistence claims, or narrative extrapolation from long-horizon tails.

## A. ECB Asset Response

The ECB asset response is directionally sensible in the point estimates: the estimated response is positive from horizons 0 through 8 and peaks at horizon 4.

Key estimates:

- Peak beta: `5.31e-07` at horizon 4
- Cumulative response through horizon 12: `1.89e-06`
- OLS and LP-IV signs agree at all six reported horizons

Interpretation: the instrumented policy shock produces a liquidity-balance-sheet response with the expected positive short- to medium-horizon direction. Because all first-stage diagnostics are weak, this should be described as directional validation only, not as a strong structural liquidity multiplier.

## B. Household Credit Transmission

Household loan responses are mixed at short horizons and negative at longer horizons in the LP-IV point estimates.

Key estimates:

- Peak absolute beta: `-1.14e-07` at horizon 12
- Cumulative response through horizon 12: `-1.75e-07`
- OLS and LP-IV signs agree at three of six horizons

Interpretation: the baseline does not provide clean evidence of persistent household-credit expansion after the identified liquidity shock. The later-horizon negative point estimates may indicate delayed balance-sheet adjustment, but weak instrument relevance prevents strong interpretation.

## C. NFC Credit Transmission

NFC loan responses turn negative after horizon 0 and become more negative at longer horizons.

Key estimates:

- Peak absolute beta: `-2.41e-07` at horizon 12
- Cumulative response through horizon 12: `-4.41e-07`
- OLS and LP-IV signs agree at all six reported horizons

Interpretation: relative to household credit, NFC credit shows a larger negative cumulative point response in the baseline. This is relevant for comparing productive intermediation against financial-balance-sheet channels, but the weak first stage means the result should be framed as a tentative pattern rather than a settled structural conclusion.

## D. Housing Transmission

Real house prices show positive LP-IV point estimates at all reported horizons.

Key estimates:

- Peak beta: `6.87e-08` at horizon 12
- Cumulative response through horizon 12: `2.60e-07`
- OLS and LP-IV signs agree at four of six horizons

Interpretation: among the non-policy responses, housing provides the clearest positive point-estimate pattern. The response appears persistent on the reported horizon grid. However, the divergence from OLS at horizons 8 and 12, together with weak relevance, means the housing result should be described as suggestive evidence of asset-price transmission, not conclusive evidence.

## E. Compensation Transmission

Real compensation is mixed at short horizons and negative at longer horizons.

Key estimates:

- Peak absolute beta: `-8.91e-08` at horizon 12
- Cumulative response through horizon 12: `-1.75e-07`
- OLS and LP-IV signs agree at all six reported horizons

Interpretation: the baseline does not show a persistent positive compensation response. The point-estimate pattern is consistent with weak or delayed real-income transmission relative to housing, but this must remain a cautious macro-structural statement because first-stage relevance is weak throughout.

## F. Relative Transmission Comparison

The baseline point estimates suggest the following relevance-limited ordering:

- ECB assets respond positively in the expected direction.
- Housing has the most persistent positive non-policy response.
- Compensation does not show sustained positive transmission.
- NFC credit is more negative cumulatively than household credit.
- Household credit is not clearly dominant over NFC credit in the baseline point estimates.

This supports a cautious working interpretation: the estimated liquidity shock appears more visible in asset-price dynamics than in compensation dynamics. It does not yet provide strong evidence that productive intermediation dominates, nor does it justify welfare or distributional claims.

All substantive thesis interpretation must keep the weak-IV qualification attached to these findings unless later robustness layers materially improve relevance.
