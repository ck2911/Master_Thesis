# Repository Cleanup Report

Date: 2026-05-15

## What Changed

The repository has been migrated away from the retired prototype and reorganized around the Euro Area / Germany SVECM architecture.

## Archived Retired Implementation

The retired implementation was moved under the archive tree and is audit-only.

Archived items include:

- Root-level retired policy and shock files.
- Extracted retired prototype datasets.
- The retired notebook pipeline.
- Legacy generated results, tables, figures, and reports.
- Obsolete source modules from the former flat `src/` layout.
- Legacy audit and extraction notes.

The archived inventory remains inside the same audit-only archive folder.

## Archived Exploratory EU/DE Phase

The prior forensic EU/DE scripts were moved to:

```text
archive/eu_de_forensic_phase/scripts/
```

The prior forensic memo was moved to:

```text
archive/eu_de_forensic_phase/eu_de_forensic_research_memo.md
```

The prior forensic outputs were retained under:

```text
archive/eu_de_forensic_phase/results/eu_de_forensic_previous_phase/
```

These remain available for audit, but the active pipeline now runs from `src/data/build_final_dataset.R` and `src/diagnostics/ecb_assets_assessment.py`.

## Active Project Roots

- Raw data: `data/raw/eu_de/`
- Processed data: `data/processed/eu_de/`
- Code: `src/`
- Configuration: `config/`
- Results: `results/`
- Documentation: `docs/`

## Cleanup Status

No retired loader or retired shock workflow remains in the active `src/` package. The old implementation is recoverable from the archive but no longer participates in the live pipeline.
