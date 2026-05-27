# Final Identification Audit

Date: 2026-05-16

## Audit Conclusion

The final architecture correctly centers high-frequency ECB monetary-policy surprises and rejects a hard-IV treatment bridge unless the bridge passes explicit relevance and stability gates. No bridge is currently accepted.

## Why The Old Design Was Retired

Quarterly ECB asset changes are persistent implementation stocks, not announcement-window innovations. The previous mixed-frequency LP-IV design could not support clean structural treatment claims.

## Current Identification Strength

Strongest layer:

```text
ECB surprise timing → monthly reduced-form response dynamics
```

Weaker layers:

- monthly hard-IV bridge candidates;
- regime decompositions;
- OLS policy-rate comparison.

These remain diagnostics and robustness checks.

## Information-Effect Screen

Every retained event records:

- rate-factor sign;
- OIS movement;
- equity-window response;
- contamination classification.

Clean and contaminated samples are written to:

```text
results/final/diagnostics/clean_event_sample.csv
results/final/diagnostics/contaminated_event_sample.csv
```

## Proxy Audit

The mixed-frequency comparison is handled with real monthly proxies, not interpolation. Accepted and rejected proxies are documented in:

```text
docs/proxy_validation.md
results/final/diagnostics/proxy_validation_tournament.csv
```

## Final Claim Boundary

Allowed:

```text
dynamic reduced-form transmission from unexpected ECB monetary-policy surprises
```

Forbidden:

```text
exact structural QE effects, exact housing-price effects, exact compensation treatment effects, welfare effects, inequality causality, redistribution magnitudes, or clean regime treatment effects
```

