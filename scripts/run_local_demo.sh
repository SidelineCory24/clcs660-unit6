#!/usr/bin/env bash
set -euo pipefail
python -m src.train_model
python -m src.evaluate_model
python -m unittest discover -s tests -v
