"""Evaluate the model on a held-out split and print reproducible metrics."""
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np

from src.train_model import load_data


def evaluate():
    """Fit on the training split, score the held-out split, and return the metrics."""
    X, y = load_data()
    # Same split, seed, and model settings as train_model.py so metrics describe the exported model.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Column 1 of predict_proba is the probability of the positive (failure) class.
    probabilities = model.predict_proba(X_test_scaled)[:, 1]
    threshold = 0.65  # must match risk_threshold in train_model.py
    predictions = (probabilities >= threshold).astype(int)
    metrics = {
        "test_rows": int(len(y_test)),
        "threshold": threshold,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        # zero_division=0 reports 0 instead of warning when a class is never predicted.
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        # ROC AUC uses raw probabilities, so it does not depend on the threshold.
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "confusion_matrix_labels_true_pred": confusion_matrix(y_test, predictions).tolist(),
    }
    print(metrics)
    print("Interpretation warning: these metrics measure separation in synthetic data, not real-world failure prediction.")
    return metrics


if __name__ == "__main__":
    evaluate()
