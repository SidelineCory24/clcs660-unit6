"""Train a baseline logistic-regression classifier on synthetic operational data."""
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.features import FEATURE_NAMES

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "synthetic_metrics.csv"
MODEL_PATH = ROOT / "model" / "model.json"


def load_data():
    rows = list(csv.DictReader(DATA_PATH.open(newline="", encoding="utf-8")))
    X = np.array([[float(row[name]) for name in FEATURE_NAMES] for row in rows])
    y = np.array([int(row["failure_within_window"]) for row in rows])
    return X, y


def train_and_export():
    X, y = load_data()
    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    classifier = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    classifier.fit(X_train_scaled, y_train)

    model = {
        "model_version": "baseline-logreg-v1",
        "algorithm": "scikit-learn LogisticRegression; standardized numeric features",
        "feature_names": FEATURE_NAMES,
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "coefficients": classifier.coef_[0].tolist(),
        "intercept": float(classifier.intercept_[0]),
        "risk_threshold": 0.65,
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
