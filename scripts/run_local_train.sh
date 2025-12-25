#!/usr/bin/env bash
set -euo pipefail
python -m src.cli.main gen-data --problem-type classification --n-rows 1000 --out data/local
python -m src.cli.main train-local --dataset-dir data/local --problem-type classification --epochs 1
