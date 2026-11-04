#!/usr/bin/env bash
set -euo pipefail
# Train, evaluate, then test. Run from the repo root: the modules below use `python -m src.*`.
# Requires `pip install -r requirements.txt` first.
python -m src.train_model
python -m src.evaluate_model
python -m unittest discover -s tests -v
