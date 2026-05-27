# Final External Identification Recommendation

Date: 2026-05-15

This memo synthesizes the strengthened ECB external-instrument layer. It does not estimate LP-IV responses, write final thesis conclusions, or force weak-IV interpretation.

## Decision

LP-IV baseline identification is frozen; diagnostics remain mandatory before response interpretation.

Official LP-IV baseline: `target_factor_market_magnitude_weighted_quarterly_sum` against `d_ecb_assets_ea_qavg`.

## Decision Matrix

| candidate | strength | stability | F_stat | partial_R2 | economic_fit | feasible |
| --- | --- | --- | --- | --- | --- | --- |
| weighted_variants | usable_F10 | unstable_or_not_supported | 13.776 | 0.230 | tests event-intensity and crisis leverage | yes |
| monthly_bridge | usable_F10 | unstable_or_not_supported | 13.387 | 0.143 | tests whether quarterly aggregation destroyed signal | yes |
| fg | usable_F10 | unstable_or_not_supported | 13.239 | 0.140 | communication channel robustness | yes |
| target | usable_F10 | regime_supported | 11.258 | 0.122 | short-rate target shock robustness | yes |
| qe | borderline | unstable_or_not_supported | 9.173 | 0.166 | closest fit to balance-sheet transmission | weak_caution |
| composite | weak | unstable_or_not_supported | 4.532 | 0.053 | captures shared ECB surprise variation | no |
| timing | weak | unstable_or_not_supported | 2.958 | 0.035 | conventional rate-news fit, weak balance-sheet fit | no |

## Required Baseline Fields

- Factor choice: `target`
- Aggregation: `market_magnitude_weighted`
- Frequency/architecture: `weighted_event_quarterly`
- First-stage target: `d_ecb_assets_ea_qavg`
- Regime restrictions: `required for review; max regime shock concentration is 53.9%`
- Weighting: `market_magnitude_weighted`
- LP-IV status: `LP-IV baseline identification is frozen; diagnostics remain mandatory before response interpretation.`

## Closed Phases

Deprecated SVECM infrastructure, FEVDs, historical decompositions, counterfactuals, welfare claims, and policy conclusions remain archived. The active stage is the frozen LP-IV thesis delivery system.
