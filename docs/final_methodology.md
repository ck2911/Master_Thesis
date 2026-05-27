# Methodology

## Shock

The main shock is the ECB target surprise, aggregated to monthly frequency and signed so that positive values mean expansionary policy news. Timing, forward-guidance, QE, and composite surprises are used as alternatives.

## Data

The monthly dataset keeps observed monthly variables at monthly frequency. Quarterly house prices, compensation per employee, and Bank Lending Survey variables remain sparse quarter-end observations. They are not filled into monthly data.

## Response Model

Monthly impulse responses are estimated with local projections. Each response is measured relative to the pre-shock month and includes lagged response controls, inflation lags, and policy-rate lags.

The horizon set is 0, 1, 3, 6, 12, and 24 months. Coefficients are scaled to a one-standard-deviation ECB surprise.

## Inference

Uncertainty is reported with HAC intervals and bootstrap checks. Cumulative responses are used to compare persistence across channels.

## Interpretation

The model compares transmission across housing credit, lending conditions, financial markets, credit aggregates, and compensation-linked variables. It does not estimate welfare, redistribution, household incidence, or exact structural mediation.
