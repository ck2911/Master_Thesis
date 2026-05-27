# Thesis Repository Master Report

## Research Objective

The thesis studies how unexpected ECB monetary-policy easing transmits after the post-COVID period of very large liquidity expansion and later tightening. The economic question is whether policy surprises mainly affect financial and housing-related variables, or whether they pass through with comparable strength into wages, compensation, and real household income.

The project tests a comparative transmission claim. It does not try to measure welfare effects or household-level redistribution. It compares response paths across channels that matter for affordability: asset prices, housing finance, lending conditions, credit, wages, and compensation pressure.

The main question is:

Does expansionary monetary policy transmit more strongly into financial assets and housing finance than into real household income?

## Economic Motivation

The post-COVID policy environment made this question especially relevant. Central-bank balance sheets expanded sharply, interest rates stayed low for a long period, and asset and housing markets absorbed a large part of the financial impulse. When inflation rose and rates increased, household affordability came under pressure from both higher financing costs and earlier asset-price increases.

The core macro-finance concern is not only whether monetary policy affects output or inflation. It is also where the first and most persistent responses appear. If housing finance, lending spreads, and financial prices react more durably than wages, expansionary policy can raise asset-side pressure without producing a matching improvement in household purchasing power.

This makes the compensation channel central. A strong wage response would suggest broader income pass-through. A weak or inconsistent wage response, beside persistent housing and financial responses, points toward asymmetric transmission through financial intermediation and balance sheets.

## Identification Strategy

The monetary shock comes from high-frequency ECB announcement surprises. These surprises are measured around policy events, before monthly macro-financial outcomes are realized. That timing gives the shock its identifying content: it captures policy news rather than slow-moving macro conditions.

The design follows the logic of an external-instrument SVAR. The policy surprise is treated as an external source of monetary variation, and the response system traces how monthly variables move after that shock. The main shock is signed so that positive values represent expansionary news.

ECB announcements can contain information about the economy as well as policy. The project therefore separates cleaner monetary events from events with possible information effects. This does not make the shock perfect, but it keeps the interpretation honest: the estimates are response paths to ECB policy-news surprises.

## Data Construction

The monetary block includes ECB surprise factors, the deposit facility rate, the Wu-Xia shadow rate, and ECB balance-sheet measures. These variables distinguish conventional rate policy from balance-sheet liquidity.

The housing block uses monthly housing-finance measures, especially house-purchase lending growth and new mortgage lending. Direct house prices are kept at their observed lower frequency, so the monthly comparison focuses on housing finance rather than claiming exact monthly house-price effects.

The wage and compensation block uses negotiated-wage-pressure measures, wage-tracker variants, and a German wage-bill proxy. These are included because the thesis needs a monthly income-side comparison, but they are interpreted as wage pressure and payroll-cost evidence rather than exact compensation per employee.

The financial-intermediation block includes mortgage and NFC lending spreads, credit stocks, and banking-survey information where available. These variables matter because monetary policy reaches households and firms through the lending system, not only through market prices.

The data choices are deliberately conservative. Quarterly variables are not filled into monthly observations. The monthly analysis uses observed monthly series or transparent monthly transformations.

## Estimation Framework

The empirical system estimates impulse responses to ECB policy-news shocks. The main estimates are monthly local projections, interpreted with the same external-shock logic used in proxy-SVAR designs.

The response horizons cover impact, short-run, medium-run, and longer-run effects. The analysis compares both point responses and accumulated responses, because the thesis is mainly about persistence across channels.

Uncertainty is reported with HAC intervals and bootstrap checks. The uncertainty layer supports the comparison of response profiles; it is not used to turn reduced-form evidence into structural welfare claims.

## Main Findings

The main finding is asymmetric transmission.

Housing and financial variables respond more strongly and more persistently than wage and compensation variables. This pattern is clearest in housing-finance growth, lending spreads, and financial-intermediation measures.

Housing-finance responses remain economically important beyond the initial policy surprise. The lending side is not just a short-run reaction: mortgage-related and credit-condition variables continue to show transmission after the impact horizon. This persistence is central for the affordability interpretation.

Financial variables also react visibly. The response pattern is consistent with policy news moving first through market prices, liquidity conditions, and credit pricing. These are the channels through which expansionary policy can raise balance-sheet values and alter borrowing conditions before households see equivalent income gains.

The compensation response is weaker. Negotiated-wage-pressure measures and wage-bill proxies provide some movement, so the labor-income channel is not absent. But the response is less durable, less consistent, and less central than the housing-finance and lending-condition evidence.

The wage result matters because it prevents a simple "monetary easing helps households through income" reading. In this evidence, the asset and housing side reacts more clearly than the compensation side.

The strongest interpretation is therefore comparative: expansionary ECB surprises appear to transmit more through financial and housing channels than through broad real-income pass-through.

## Interpretation

The results fit a financialized view of monetary transmission. Policy news affects the value and cost of financial claims quickly, while wage and compensation adjustment is slower, negotiated, and more institutionally constrained.

This creates an affordability-relevant asymmetry. If housing finance and asset-side variables respond persistently while wages respond weakly, monetary easing can support asset-price and credit channels without a matching improvement in real household income.

The findings also highlight the role of financial intermediation. Lending spreads and credit variables help explain why the housing response is not only a market-price story. Banks and lending conditions form the practical channel through which policy news reaches housing finance.

The thesis should therefore be read as evidence on transmission patterns, not as a direct measure of welfare, inequality, or redistribution.

## Robustness

The main result is checked with alternative ECB surprise measures, cleaner event samples, rolling and recursive estimates, crisis and COVID exclusions, and alternative wage and housing-finance proxies.

The exact magnitude changes across specifications, as expected in monthly macro-financial data. The direction of the evidence is more stable: housing finance and lending conditions remain more persistent than the main compensation proxies.

The robustness work supports the central hierarchy without removing the identification boundary. The evidence is strongest for comparative transmission, not for exact structural mediation.

## Conclusion

The repository supports a clear thesis argument: post-COVID ECB monetary-policy surprises transmit more visibly through financial markets, lending conditions, and housing finance than through wages and real compensation.

The econometric design keeps the claim narrow but meaningful. It identifies dynamic responses to external monetary-policy news and uses those responses to compare channels. Within that boundary, the evidence points to persistent asset-side and housing-finance transmission with weaker wage pass-through.
