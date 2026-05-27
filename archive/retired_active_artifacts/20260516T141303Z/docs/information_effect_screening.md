# Information-Effect Screening

Date: 2026-05-15

This is a lightweight Jarocinski-Karadi-style screen, not a full decomposition.

## Event Logic

- Same-sign rate and equity responses are flagged as potential central-bank information shocks.
- Opposite-sign rate and equity responses are flagged as potential pure monetary shocks.
- Zero or missing market responses are flagged as ambiguous or unclassified.

## Event Counts

| instrument | observations |
| --- | --- |
| potential_pure_monetary_shock | 133 |
| potential_information_shock | 102 |
| ambiguous_zero_response | 9 |

## Regime Summary

| instrument | target_equation | observations | partial_R2 |
| --- | --- | --- | --- |
| covid | potential_information_shock | 9 | 0.450 |
| covid | potential_pure_monetary_shock | 11 | 0.550 |
| euro_crisis | ambiguous_zero_response | 1 | 0.017 |
| euro_crisis | potential_information_shock | 25 | 0.417 |
| euro_crisis | potential_pure_monetary_shock | 34 | 0.567 |
| gfc | potential_information_shock | 11 | 0.579 |
| gfc | potential_pure_monetary_shock | 8 | 0.421 |
| pre_gfc | potential_information_shock | 37 | 0.474 |
| pre_gfc | potential_pure_monetary_shock | 41 | 0.526 |
| qe_era | ambiguous_zero_response | 7 | 0.175 |
| qe_era | potential_information_shock | 14 | 0.350 |
| qe_era | potential_pure_monetary_shock | 19 | 0.475 |
| tightening_regime | ambiguous_zero_response | 1 | 0.037 |
| tightening_regime | potential_information_shock | 6 | 0.222 |
| tightening_regime | potential_pure_monetary_shock | 20 | 0.741 |

## Use in Thesis

These flags support interpretation and robustness screening only. They do not replace the ABGMR external instrument and do not unlock final response interpretation.
