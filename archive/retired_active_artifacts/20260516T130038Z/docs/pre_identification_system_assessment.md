# Pre-Identification System Assessment

Date: 2026-05-15

This assessment closes the pre-identification stress-testing phase. It does not estimate the final SVECM.

## 1. Which Variables Belong Inside Beta?

Preferred beta block:

- `ln_ecb_assets_ea_stock`
- `ln_hh_loans_ea_stock`
- `ln_nfc_loans_ea_stock`
- `ln_house_price_de_real`
- `ln_compensation_ea20_real`

Rationale: ECB assets reject weak exogeneity in both samples, so the data do not support treating liquidity as a purely external long-run forcing variable. Household loans, NFC loans, real house prices, and real compensation remain the economically coherent credit-asset-purchasing-power block.

Excluded from baseline beta:

- `wx_shadow_rate`: weakly exogenous in the baseline policy extension.
- `dfr_eop`: rejects weak exogeneity if forced into beta, but should remain a policy/regime variable outside beta because the post-2022 rate normalization is not a stable long-run equilibrium relation.
- `ln_dax_real_de`: weakly exogenous and does not improve rank stability enough to justify baseline inclusion.

## 2. Which Variables Are Weakly Exogenous?

Alpha restriction results:

| Candidate | Sample | LR | p-value | Interpretation |
|---|---:|---:|---:|---|
| `ln_ecb_assets_ea_stock` | baseline | 7.217 | 0.027 | Reject weak exogeneity |
| `ln_ecb_assets_ea_stock` | robustness | 10.672 | 0.001 | Reject weak exogeneity |
| `wx_shadow_rate` | baseline | 1.230 | 0.541 | Weak exogeneity not rejected |
| `dfr_eop` | robustness | 25.039 | 0.000 | Reject weak exogeneity if included |
| `ln_dax_real_de` | baseline | 0.912 | 0.339 | Weak exogeneity not rejected |
| `ln_dax_real_de` | robustness | 0.193 | 0.660 | Weak exogeneity not rejected |

Operational interpretation: `wx_shadow_rate` and `ln_dax_real_de` are weakly exogenous candidates. `dfr_eop` is not weakly exogenous in the expanded long-run test, but remains better handled outside beta as a short-run/conventional-policy robustness control.

## 3. Is ECB Liquidity Endogenous Or Forcing?

Baseline answer: endogenous long-run equilibrium variable.

The formal alpha tests reject `alpha_ecb = 0` in both the baseline and robustness samples. That means ECB assets adjust to the long-run relation and should not be treated as purely weakly exogenous in the main specification.

Important caveat: collinearity is borderline, especially ECB assets versus household loans, and rolling rank behavior is unstable around COVID and tightening windows. Therefore the forcing-process interpretation should be retained as a robustness specification, not as the baseline.

## 4. Is DAX Structurally Useful?

No for the baseline.

DAX is useful as an expanded asset-price robustness variable, but not as a core beta variable. It fails to reject weak exogeneity, contributes little to stable rank selection, and produces extreme first-vector beta coefficients in the expanded system. It should be excluded from the baseline beta and used only for robustness checks on equity-asset-price transmission.

## 5. What Is The Stable Rank?

Conservative final rank: `r = 1`.

Evidence:

- Robustness sample, Block 2 (`Block 1 + ECB assets`): median rank 1 and unique trace rank 1 across the rank grid.
- Expanded Block 3: robustness median rank 1, but rank can move to 2.
- Baseline sample often supports rank 2, but trace/max-eigen disagreement and rolling-window instability warn against using this as the final default.
- Rolling windows show elevated ranks around COVID-era windows, consistent with artificial rank inflation from regime shifts.

Recommended handling: estimate the final baseline with `r = 1`; report `r = 2` as a sensitivity case for the 2005Q1-2022Q2 baseline sample.

## 6. Which System Is Statistically Defensible?

Defensible baseline system:

```text
ln_ecb_assets_ea_stock
ln_hh_loans_ea_stock
ln_nfc_loans_ea_stock
ln_house_price_de_real
ln_compensation_ea20_real
```

with rank `r = 1` as the conservative final setting.

Required robustness systems:

- ECB assets outside beta / short-run forcing block.
- DAX expanded block.
- Household-credit-only and NFC-credit-only blocks.
- Rank `r = 2` sensitivity for the shorter baseline sample.

Collinearity status: all candidate systems are borderline, none are classified as unusable. This is workable, but final structural interpretation must be parsimonious.

## 7. Which Identification Strategy Is Feasible?

Feasible baseline identification:

```text
External-Instrument SVECM
+ Altavilla-style ECB monetary-policy surprises
+ quarterly aggregation
```

The EA-MPD / ABGMR route is public, Euro Area specific, event-date based, and compatible with quarterly aggregation. The Jarociński-Karadi information-effect framework is conceptually important but too heavy for the baseline implementation unless the thesis expands into a separate high-frequency replication project.

## 8. Final Thesis Architecture

Final recommended architecture:

```text
External-Instrument SVECM

Endogenous long-run block:
ECB assets
household loans
NFC loans
German real house prices
EA20 real compensation

Policy variables outside beta:
Wu-Xia shadow rate for baseline monetary stance
ECB deposit facility rate for post-2022 robustness

External instrument:
ECB high-frequency monetary-policy surprise
aggregated to quarters

Baseline rank:
r = 1

Robustness:
r = 2 baseline-sample sensitivity
ECB-assets-as-forcing specification
DAX expanded asset-price block
Jarociński-Karadi information-effect discussion or lightweight sign-screen
```

## Deliverables Produced

- `docs/final_data_source_registry.md`
- `docs/ecb_external_instrument_feasibility_memo.md`
- `results/stress_testing/weak_exogeneity_report.md`
- `results/stress_testing/beta_stability/beta_stability_report.md`
- `results/stress_testing/beta_stability/eigenvalue_evolution_plots.png`
- `results/stress_testing/beta_stability/beta_coefficient_drift_plots.png`
- `results/stress_testing/collinearity_diagnostics.md`
- `results/stress_testing/rank_robustness_matrix.xlsx`

Final SVECM estimation should begin only after the ECB surprise instrument is imported, quarter-aggregated, and subjected to first-stage relevance diagnostics.
