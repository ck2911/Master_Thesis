# Thesis Repository Master Report

## Research Objective

The thesis studies how unexpected ECB monetary-policy easing transmits through macro-financial channels in the post-COVID monetary environment. The central question is whether policy-news shocks transmit more strongly through housing-credit and selected financial-intermediation variables than through compensation-linked real-economy variables.

The project tests a comparative transmission claim. It compares response paths across housing credit, lending conditions, credit aggregates, financial markets, and compensation-linked proxies. It does not try to measure household welfare effects, inequality, redistribution, or borrower-level incidence.

The main question is:

```text
Did post-COVID ECB monetary easing transmit more strongly through housing-credit
and financial-intermediation channels than through compensation-linked
real-economy variables?
```

## Repository Entry Points

The canonical empirical walkthrough is `1. thesis_master_notebook.ipynb` at the repository root. The leading `1. ` keeps the notebook at the top of sorted file views, and the former `notebooks/` folder is not part of the active workflow.

Rebuilds start from `python scripts/run_full_pipeline.py`, and the thesis document is compiled from `LATEX/` with `make pdf` or `scripts/compile.sh`. The LaTeX workspace reads the same repository-level outputs as the notebook and does not own separate empirical copies.

## Economic Motivation

The post-COVID policy environment made this question especially relevant. Central-bank balance sheets expanded sharply, interest rates stayed low for a long period, and the subsequent tightening cycle changed borrowing conditions quickly. The macro-finance concern is where policy-news responses are clearest and most persistent: in intermediation and housing credit, or in compensation-linked real-economy variables.

The compensation block remains important, but it is a comparison block rather than a welfare test. A strong and persistent compensation-linked response would suggest broader income-side transmission. A weaker or less consistent response, beside persistent housing-credit and lending-condition responses, points toward heterogeneous transmission through financial intermediation and balance sheets.

## Identification Strategy

The monetary shock comes from high-frequency ECB announcement surprises. These surprises are measured around policy events, before monthly macro-financial outcomes are realized. The main shock is signed so that positive values represent expansionary news.

ECB announcements can contain information about the economy as well as policy. The project therefore separates cleaner monetary events from events with possible information effects. This does not make the shock perfect, but it keeps the interpretation honest: the estimates are response paths to ECB policy-news surprises.

The DAX sign problem is part of this identification boundary. A negative equity response after an easing surprise may indicate that the announcement contains adverse macroeconomic information as well as accommodative policy news. Equity responses are therefore interpreted as mixed financial-market evidence, not as a simple asset-price channel.

## Data Construction

The monetary block includes ECB surprise factors, the deposit facility rate, the Wu-Xia shadow rate, and ECB balance-sheet measures. These variables distinguish conventional rate policy from balance-sheet liquidity.

The housing-credit block uses monthly housing-credit measures, especially house-purchase lending growth and pure-new mortgage lending. Direct house prices are kept at their observed lower frequency, so the monthly comparison focuses on housing credit rather than claiming exact monthly house-price effects.

The compensation-linked block uses negotiated-wage-pressure measures, wage-tracker variants, and a German wage-bill proxy. These variables are interpreted as wage pressure and payroll-cost evidence rather than exact compensation per employee.

The financial-intermediation block includes mortgage and NFC lending spreads, lending rates, credit stocks, and banking-survey information where available. These variables matter because monetary policy reaches households and firms through lending conditions, not only through market prices.

The data choices are deliberately conservative. Quarterly variables are not filled into monthly observations. The monthly analysis uses observed monthly series or transparent monthly transformations.

## Estimation Framework

The empirical system estimates impulse responses to ECB policy-news shocks. The main estimates are monthly local projections, interpreted with the same external-shock logic used in proxy-SVAR designs.

The response horizons cover impact, short-run, medium-run, and longer-run effects. The analysis compares both point responses and accumulated responses, because the thesis is mainly about persistence across channels.

Uncertainty is reported with HAC intervals and bootstrap checks. The uncertainty layer supports the comparison of response profiles; it is not used to turn reduced-form evidence into structural welfare claims.

## Main Findings

The main finding is heterogeneous transmission.

House-purchase lending growth is the clearest and most persistent response. It is positive through medium horizons and remains positive in accumulated terms through h24. This result is the core empirical contribution.

Lending spreads and intermediation variables support the mechanism interpretation. Mortgage and NFC spreads show durable positive accumulated responses, while broad credit stocks are weaker. The evidence points to sectorally differentiated transmission rather than a generic credit-quantity response.

Pure-new house-purchase loans provide a flow-based robustness check. They are more volatile and shorter in sample, so they do not replace the stock-based house-purchase lending growth result. The divergence between the two is interpreted as a stock-flow distinction: credit growth captures sustained financing conditions, while pure-new lending captures immediate origination behavior.

Financial-market responses are mixed. The DAX response is negative at medium and longer horizons, which is consistent with possible information effects in ECB communications. ECB assets provide liquidity-stock context but are not a strong persistence pillar.

Compensation-linked responses are weaker and less consistent. Wage-pressure measures and wage-bill proxies provide some movement, so the labor-income channel is not absent. The comparative result is that the compensation-linked block does not show the same durable response profile as housing credit and lending conditions.

## Interpretation

The strongest interpretation is comparative: expansionary ECB policy-news shocks appear to transmit most clearly through housing-credit and selected financial-intermediation channels, while evidence for broad compensation-linked real-economy transmission is weaker and less consistent.

The findings highlight the role of financial intermediation. Lending spreads and credit variables help explain why the housing-credit response is not only a market-price story. Banks and lending conditions form the practical channel through which policy news reaches housing credit.

The thesis should therefore be read as evidence on channel-specific transmission patterns, not as a direct measure of welfare, inequality, redistribution, or structural mediation.

## Robustness

The main result is checked with alternative ECB surprise measures, cleaner event samples, rolling and recursive estimates, crisis and COVID exclusions, and alternative wage and housing-credit proxies.

The exact magnitude changes across specifications, as expected in monthly macro-financial data. The direction of the evidence is more stable: house-purchase lending growth and lending conditions remain more persistent than the main compensation-linked proxies.

The robustness work supports the central hierarchy without removing the identification boundary. The evidence is strongest for comparative transmission, not for exact structural mediation.

## Conclusion

The repository supports a clear thesis argument: post-COVID ECB monetary-policy surprises transmit most clearly and persistently through housing credit and selected intermediation variables, while compensation-linked real-economy evidence is weaker and less consistent.

The econometric design keeps the claim narrow but meaningful. It identifies dynamic responses to external monetary-policy news and uses those responses to compare channels. Within that boundary, the evidence points to heterogeneous macro-financial transmission centered on housing-credit amplification.
