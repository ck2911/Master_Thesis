#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LATEX_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${LATEX_DIR}"
mkdir -p build

latexmk main.tex

printf 'PDF written to %s\n' "${LATEX_DIR}/main.pdf"
