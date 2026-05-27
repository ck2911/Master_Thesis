#!/usr/bin/env bash
set -euo pipefail

python -m src.data.ecb_monetary_surprises "$@"
