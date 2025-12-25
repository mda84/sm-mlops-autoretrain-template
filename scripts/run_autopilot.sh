#!/usr/bin/env bash
set -euo pipefail
python -m src.cli.main autopilot-run --dataset-s3 "$1" --problem-type classification
