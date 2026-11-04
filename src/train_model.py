"""Train a baseline logistic-regression classifier on synthetic operational data."""
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.features import FEATURE_NAMES

# Resolve paths from this file so the script works regardless of the current directory.
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "synthetic_metrics.csv"
MODEL_PATH = ROOT / "model" / "model.json"


def load_data():
    """Return the feature matrix X and failure labels y from the synthetic CSV."""
    rows = list(csv.DictReader(DATA_PATH.open(newline="", encoding="utf-8")))
    X = np.array([[float(row[name]) for name in FEATURE_NAMES] for row in rows])
    y = np.array([int(row["failure_within_window"]) for row in rows])
    return X, y


def train_and_export():
    """Train on the training split and write the JSON model used by Lambda inference."""
    X, y = load_data()
    # Stratify so the minority (failure) class appears in both splits; the fixed seed
    # (42) makes the split reproducible and must match evaluate_model.py.
    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    # Fit the scaler on training data only, to avoid leaking test-set statistics.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    # class_weight="balanced" compensates for failures being the minority class.
    classifier = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    classifier.fit(X_train_scaled, y_train)

    # Plain JSON (no pickle) keeps the artifact inspectable and safe to load in Lambda.
    model = {
        "model_version": "baseline-logreg-v1",
        "algorithm": "scikit-learn LogisticRegression; standardized numeric features",
        "feature_names": FEATURE_NAMES,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "coefficients": classifier.coef_[0].tolist(),
        "intercept": float(classifier.intercept_[0]),
        "risk_threshold": 0.65,  # keep in sync with evaluate_model.py
        "training_rows": int(len(X_train)),
        "data_note": "Synthetic course-project data; not validated production telemetry.",
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    print(f"Trained on {len(X_train)} rows; model exported to {MODEL_PATH}")
    print("Model is a prototype. Evaluate using held-out metrics before interpreting predictions.")
    return model


if __name__ == "__main__":
    train_and_export()
