# ECB External-Instrument Feasibility Memo

Date: 2026-05-15

This memo evaluates feasible external instruments for the planned EU/DE External-Instrument SVECM. It is intentionally pre-estimation: the goal is to select an implementable identification track after system stress testing, not to run final structural IRFs.

## Evidence Base

- Altavilla, Brugnolini, Gürkaynak, Motto, and Ragusa construct the Euro Area Monetary Policy Event-Study Database (EA-MPD), which contains intraday asset-price changes around the ECB policy decision and press conference windows. The ECB working paper describes OIS, Bund, sovereign yield, stock-index, bank-stock, and euro exchange-rate coverage, plus separate press-release, press-conference, and combined monetary-event windows. Source: [ECB Working Paper No. 2281](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2281~3303fd281b.en.pdf).
- The EA-MPD data link is publicly exposed from the publication page as an ECB-hosted Excel annex: [Dataset_EA-MPD.xlsx](https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx).
- Giuseppe Ragusa maintains downloadable ABGMR factor CSV vintages for press-release and press-conference factors. As inspected on 2026-05-15, the page lists vintages through 2025-10-30 and identifies Target, Timing, Forward Guidance, and QE factor normalizations. Source: [Monetary policy factors](https://gragusa.org/factors/).
- Jarociński and Karadi identify monetary-policy versus central-bank-information shocks using high-frequency comovement of interest-rate and stock-price surprises. Source: [paper PDF](https://peterkaradi.github.io/website/Published/JarocinskiKaradi.pdf).
- The AEA hosts a replication package for Jarociński and Karadi, with the page noting migration to ICPSR and providing a dataset download entry. Source: [AEA replication package page](https://www.aeaweb.org/journals/dataset?id=10.1257/mac.20180090).

## Feasibility Matrix

| Criterion | Altavilla / EA-MPD / ABGMR Factors | Jarociński-Karadi |
|---|---|---|
| Data availability | High. ECB-hosted EA-MPD workbook is public; factor CSV vintages are separately downloadable. | Medium. AEA replication package is public, but current page says the package is being migrated to ICPSR; direct extension to 2025 would require fresh high-frequency market data. |
| Replicability | High if using published factors; medium if re-estimating rotations from EA-MPD. | Medium-low for full replication. The sign-decomposition logic is clear, but exact replication requires careful handling of high-frequency interest-rate and equity surprises plus VAR/sign restrictions. |
| Coding burden | Medium. Need downloader/parser, event-date to quarter mapping, factor choice, aggregation rule, and first-stage instrument diagnostics. | High. Full implementation requires reconstructing or importing high-frequency surprises, decomposing monetary and information shocks, and adapting the identification to the quarterly SVECM. |
| Sample compatibility | Strong for baseline 2005Q1-2022Q2. Strong for most robustness work; inspected factor vintages reach 2025-10-30, so the very end of 2025Q4 must be checked before final estimation. | Partial. Published replication is not naturally maintained as a live 2005-2025 ECB-quarterly instrument source. Updating to 2025 is a separate data project. |
| Identification purity | Good for ECB monetary-policy surprises, especially with separate Target, Timing, Forward Guidance, and QE dimensions. Does not fully purge central-bank information shocks by itself. | Conceptually strongest for separating pure monetary shocks from information shocks. This is valuable for interpretation but costly for a thesis-scale baseline. |
| Thesis feasibility | High. Best baseline external-instrument route. | Medium as discussion or robustness framework; low as a full baseline replication within the current repo. |

## Track A: Altavilla-Style Baseline

The Altavilla route is the most defensible baseline for this repository because it is Euro Area specific, public, event-date based, and already decomposes ECB communication into policy-relevant dimensions. The dataset is designed around ECB institutional timing: the policy decision is separated from the press conference, which maps naturally to distinct policy surprises.

Implementation plan:

1. Download EA-MPD and/or the ABGMR factor CSV vintage selected for the thesis cutoff.
2. Keep event-level observations with valid dates and factor values.
3. Map event dates to quarters and aggregate surprises by sum within quarter. A sum is preferred for an external instrument because multiple event surprises in one quarter are cumulative news shocks; quarterly mean can be retained as robustness.
4. Start with a parsimonious instrument:
   - baseline: Timing or Target/Timing composite for conventional policy surprise;
   - robustness: FG and QE factors, especially post-2014.
5. Run instrument relevance diagnostics against the SVECM policy equation before structural IRFs.

Feasibility conclusion: implementable and thesis-defensible. This should be the baseline external instrument family.

## Track B: Jarociński-Karadi Information-Effect Framework

Jarociński-Karadi is important because it addresses a real identification problem: central-bank announcements contain both policy news and information about the economic outlook. Their key sign logic is that a monetary tightening raises rates and lowers stocks, while a positive central-bank-information shock raises both rates and stocks.

For this thesis, a full JK replication is probably not the right baseline. The current repo is quarterly, EU/DE-focused, and already needs substantial pre-identification stabilization. Full JK replication would add a separate high-frequency identification project with more data dependencies and sign-restricted shock decomposition before the SVECM can even begin.

Practical use:

- Discuss JK as the main information-effect critique of high-frequency monetary instruments.
- Optionally implement a lightweight robustness screen: classify ECB event surprises by the sign of rate and equity comovement if the needed EA-MPD OIS and STOXX fields are cleanly imported.
- Do not make full JK replication the baseline unless the thesis scope expands.

Feasibility conclusion: conceptually strong, but best treated as an interpretation and robustness framework rather than the main implementation.

## Recommended Identification Path

The final architecture should converge toward:

```text
External-Instrument SVECM
+ ECB monetary-policy surprises
+ quarterly aggregation
```

Baseline instrument: Altavilla-style EA-MPD/ABGMR monetary-policy factors.

Robustness/discussion: Jarociński-Karadi information-effect logic, with full replication explicitly out of baseline scope unless new high-frequency data work is added.
