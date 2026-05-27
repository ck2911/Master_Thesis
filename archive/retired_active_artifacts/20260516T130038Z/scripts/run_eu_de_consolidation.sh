#!/usr/bin/env bash
set -euo pipefail

Rscript src/data/build_final_dataset.R
MPLCONFIGDIR=/private/tmp/codex-mpl python3 -m src.diagnostics.ecb_assets_assessment
