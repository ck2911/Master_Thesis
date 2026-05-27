# Euro Area / Germany Data Requirements

The active repository now contains the required Euro Area / Germany raw datasets under `data/raw/eu_de/` and builds the canonical quarterly model dataset under `data/processed/eu_de/`.

## Source Hierarchy

1. ECB / Eurosystem
2. Bundesbank
3. Eurostat
4. BIS
5. OECD
6. Market-data CSVs only where official macro-financial alternatives are unavailable

## Active Raw Inputs

- Wu-Xia Euro Area shadow rate.
- Central Bank Assets for Euro Area, weekly stock.
- ECB Deposit Facility Rate.
- ECB MFI household loan stock.
- ECB MFI NFC loan stock.
- ECB Bank Lending Survey credit standards for enterprises.
- ECB Bank Lending Survey credit standards for households.
- German residential property prices.
- DAX 40 monthly close.
- Euro Area 20 compensation per employee.
- German retail volume growth.
- Eurostat HICP rows for Germany, EA20, and EA.

## Still Needed Before Final Identification

The final SVECM identification layer still requires an external ECB monetary-policy surprise instrument. It should be stored as a raw input and loaded through `src/svecm/external_instruments.py` once selected.
