# Weak-IV Structural Interpretation Memo

This memo summarizes what can be credibly learned after applying weak-IV robust governance to the frozen canonical LP-IV baseline.

The correct thesis position is:

**evidence on ECB liquidity transmission asymmetry under constrained identification**

not:

**proof of precise causal magnitudes or distributional welfare effects**

## 1. Weak-IV Robust Inference Result

The Anderson-Rubin layer was implemented for every frozen baseline response-horizon cell.

Baseline classification result:

| Classification | Count |
|---|---:|
| robust_signal | 0 |
| directional_only | 30 |
| unidentified | 0 |

Several AR point-null tests reject `beta = 0`, but every inverted AR interval is unbounded. Under the classification rule, this prevents any baseline cell from being labeled a clean `robust_signal`.

Interpretation:

- coefficient magnitudes remain weak-IV fragile
- signs and persistence patterns may still be informative when stable across comparison layers
- all baseline claims must be directional and explicitly weak-IV qualified

## 2. OLS Versus LP-IV Directional Comparison

OLS local projections use the same horizon construction, controls, sample, and deterministic terms as the LP-IV baseline. The only difference is the absence of instrumentation.

Directional agreement by response:

| Response | Sign Agreement |
|---|---:|
| ECB assets | 6 / 6 |
| Household loans | 3 / 6 |
| NFC loans | 6 / 6 |
| Housing | 4 / 6 |
| Compensation | 6 / 6 |

Persistence/cumulative direction agreement remains high for ECB assets, housing, NFC loans, and compensation. Household-credit evidence is less stable at short horizons.

Interpretation:

- ECB assets, NFC loans, and compensation have the strongest OLS/LP-IV sign alignment
- housing remains cumulatively aligned even though tail signs differ in some OLS comparisons
- household lending is not directionally dominant relative to NFC lending

## 3. Directional Stability

The sign-stability matrix compares baseline LP-IV, OLS LPs, DAX robustness, regime interactions, cumulative IRFs, lag sensitivity, and horizon sensitivity.

Key directional patterns:

- Housing is positive at every baseline horizon and has a positive cumulative response.
- Compensation is negative at four of six baseline horizons and has a negative cumulative response.
- NFC credit is negative at five of six baseline horizons and is highly persistent in the negative direction.
- Household credit is negative at five of six baseline horizons but has weaker OLS sign agreement.
- ECB assets are positive through horizon 8 and turn negative at horizon 12.

The housing-versus-compensation comparison survives as a directional asymmetry:

`housing positive and persistent`

versus

`compensation mixed early, negative cumulatively`

This is a macro-financial transmission pattern, not a welfare claim.

## 4. Regime Mutation

Regime evidence remains weak-IV constrained. COVID and baseline-window tightening are generally not feasible for AR inference because of short regime samples. Pre-QE and QE are more informative, but still weak-identification environments.

Regime patterns:

- Housing cumulative response is positive in pre-QE and QE, with a larger QE cumulative point estimate.
- Compensation cumulative response is negative in pre-QE and QE.
- NFC credit remains negative cumulatively in pre-QE and QE.
- COVID concentrates identification variation, so COVID-specific interpretation must be especially cautious.
- Baseline-window tightening is too short for credible regime-specific AR interpretation.

The regime layer cautiously supports the idea that QE-era transmission is more visible in housing than compensation. It does not support strong regime-causal magnitudes.

## 5. Final Transmission Ranking

The ranking combines directional persistence, cumulative persistence, regime consistency, sign stability, and weak-IV status.

| Channel | Direction | Weak-IV Status |
|---|---|---|
| NFC credit | negative | directional_only |
| Housing | positive | directional_only |
| HH credit | negative | directional_only |
| Compensation | negative | directional_only |
| ECB assets | positive | directional_only |

For the central thesis comparison, housing ranks above compensation in stability and persistence. That supports the constrained statement that asset-price transmission is more systematically visible than compensation transmission in the frozen baseline evidence.

## 6. Interpretation Rules Going Forward

Allowed:

- directional transmission
- balance-sheet propagation
- relative housing versus compensation strength
- regime mutation
- macro-financial asymmetry

Forbidden:

- precise causal magnitudes
- welfare claims
- inequality causality
- affordability causality
- political conclusions
- normative central-bank judgments

## Bottom Line

The evidence does not overcome weak identification. It does, however, support a disciplined directional thesis:

ECB liquidity shocks show more persistent and stable transmission through housing and macro-financial balance-sheet channels than through real compensation dynamics, but this conclusion must be framed as structural pattern robustness under weak-IV constraints rather than precise causal measurement.
