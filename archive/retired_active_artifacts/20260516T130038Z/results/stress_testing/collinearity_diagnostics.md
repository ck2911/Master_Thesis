# Collinearity Diagnostics

The system is trend dominated, so diagnostics are evaluated on levels, logs, first-differenced logs, the estimated cointegrating space, rolling pairwise correlations, and principal components.

## Condition Numbers

| system | level_condition_number | log_condition_number | differenced_log_condition_number | cointegrating_space_condition_number |
| --- | --- | --- | --- | --- |
| block_1_credit_housing_income | 7.355 | 8.010 | 2.521 | 1.000 |
| block_2_plus_ecb_assets | 18.091 | 15.810 | 2.621 | 1.000 |
| block_3_plus_dax | 20.081 | 24.136 | 2.740 | 1.000 |
| block_4_household_credit_only | 16.748 | 13.397 | 1.658 | 1.000 |
| block_5_nfc_credit_only | 10.472 | 8.020 | 1.684 | 1.000 |
| block_6_real_variables_only | 3.889 | 3.695 | 1.285 | 1.000 |

## Principal-Component Structure

| system | component | variance_share | cumulative_share |
| --- | --- | --- | --- |
| block_1_credit_housing_income | PC1 | 0.755 | 0.755 |
| block_1_credit_housing_income | PC2 | 0.178 | 0.933 |
| block_1_credit_housing_income | PC3 | 0.055 | 0.988 |
| block_2_plus_ecb_assets | PC1 | 0.793 | 0.793 |
| block_2_plus_ecb_assets | PC2 | 0.143 | 0.936 |
| block_2_plus_ecb_assets | PC3 | 0.049 | 0.984 |
| block_3_plus_dax | PC1 | 0.782 | 0.782 |
| block_3_plus_dax | PC2 | 0.128 | 0.910 |
| block_3_plus_dax | PC3 | 0.047 | 0.958 |
| block_4_household_credit_only | PC1 | 0.862 | 0.862 |
| block_4_household_credit_only | PC2 | 0.074 | 0.936 |
| block_4_household_credit_only | PC3 | 0.059 | 0.995 |
| block_5_nfc_credit_only | PC1 | 0.762 | 0.762 |
| block_5_nfc_credit_only | PC2 | 0.166 | 0.927 |
| block_5_nfc_credit_only | PC3 | 0.061 | 0.988 |
| block_6_real_variables_only | PC1 | 0.851 | 0.851 |
| block_6_real_variables_only | PC2 | 0.087 | 0.938 |
| block_6_real_variables_only | PC3 | 0.062 | 1.000 |

## Rolling Correlation Summary

| pair | correlation |
| --- | --- |
| ln_dax_real_de vs ln_hh_loans_ea_stock | min=0.227; mean=0.567; max=0.820 |
| ln_dax_real_de vs ln_house_price_de_real | min=0.026; mean=0.629; max=0.818 |
| ln_ecb_assets_ea_stock vs ln_hh_loans_ea_stock | min=0.836; mean=0.920; max=0.967 |
| ln_ecb_assets_ea_stock vs ln_nfc_loans_ea_stock | min=-0.570; mean=0.329; max=0.892 |
| ln_hh_loans_ea_stock vs ln_house_price_de_real | min=-0.591; mean=0.658; max=0.981 |
| ln_nfc_loans_ea_stock vs ln_house_price_de_real | min=-0.776; mean=-0.040; max=0.804 |

## System Conclusions

| system | max_abs_level_log_correlation | pc1_variance_share | worst_condition_number | conclusion |
| --- | --- | --- | --- | --- |
| block_1_credit_housing_income | 0.851 | 0.755 | 8.010 | borderline |
| block_2_plus_ecb_assets | 0.950 | 0.793 | 18.091 | borderline |
| block_3_plus_dax | 0.950 | 0.782 | 24.136 | borderline |
| block_4_household_credit_only | 0.950 | 0.862 | 16.748 | borderline |
| block_5_nfc_credit_only | 0.873 | 0.762 | 10.472 | borderline |
| block_6_real_variables_only | 0.808 | 0.851 | 3.889 | borderline |

Classification rule: `unusable` if standardized condition number exceeds 1000, maximum absolute log-level correlation exceeds 0.98, or PC1 exceeds 90 percent of variance; `borderline` if condition number exceeds 100, correlation exceeds 0.90, or PC1 exceeds 75 percent.

Supporting files: `collinearity_condition_numbers.csv`, `collinearity_pca_variance.csv`, `rolling_correlations.csv`, and `rolling_correlation_diagnostics.png`.
