"""Small, dependency-free logistic-regression inference runtime for AWS Lambda."""
import math
from src.features import FEATURE_NAMES, validate_features


def predict_failure_risk(record, model):
    """Return probability and a threshold-based risk label for a validated record."""
    values = validate_features(record)
    means = model["scaler_mean"]
    scales = model["scaler_scale"]
    coefficients = model["coefficients"]

    if not (len(means) == len(scales) == len(coefficients) == len(FEATURE_NAMES)):
        raise ValueError("Model feature dimensions do not match expected features")

    score = float(model["intercept"])
    for value, mean, scale, coefficient in zip(values, means, scales, coefficients):
        safe_scale = float(scale) if float(scale) != 0 else 1.0
        score += ((value - float(mean)) / safe_scale) * float(coefficient)

    # Numerically stable sigmoid.
    if score >= 0:
        probability = 1.0 / (1.0 + math.exp(-min(score, 700)))
    else:
        exp_score = math.exp(max(score, -700))
        probability = exp_score / (1.0 + exp_score)

    threshold = float(model.get("risk_threshold", 0.65))
    return {
        "predicted_failure_probability": round(probability, 6),
        "risk_threshold": threshold,
        "risk_level": "ELEVATED" if probability >= threshold else "NORMAL",
        "model_version": model.get("model_version", "unversioned"),
    }
