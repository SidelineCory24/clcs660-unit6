"""Small, dependency-free logistic-regression inference runtime for AWS Lambda."""
# Only the standard library is used so the Lambda package does not need scikit-learn;
# the model is the JSON file exported by train_model.
import math
from src.features import FEATURE_NAMES, validate_features


def predict_failure_risk(record, model):
    """Return probability and a threshold-based risk label for a validated record."""
    # Raises ValueError on bad input, so invalid records never produce a prediction.
    values = validate_features(record)
    means = model["scaler_mean"]
    scales = model["scaler_scale"]
    coefficients = model["coefficients"]

    # Guard against a stale or mismatched model file before zip() silently truncates.
    if not (len(means) == len(scales) == len(coefficients) == len(FEATURE_NAMES)):
        raise ValueError("Model feature dimensions do not match expected features")

    # Standardize each feature, then take the weighted sum: intercept + sum(coefficient * z).
    score = float(model["intercept"])
    for value, mean, scale, coefficient in zip(values, means, scales, coefficients):
        # scikit-learn stores a zero scale for constant features; avoid dividing by zero.
        safe_scale = float(scale) if float(scale) != 0 else 1.0
        score += ((value - float(mean)) / safe_scale) * float(coefficient)

    # Numerically stable sigmoid. The +/-700 clamp keeps math.exp finite (it overflows near 709).
    if score >= 0:
        probability = 1.0 / (1.0 + math.exp(-min(score, 700)))
    else:
        exp_score = math.exp(max(score, -700))
        probability = exp_score / (1.0 + exp_score)

    # 0.65 is the fallback only when the model file does not specify a threshold.
    threshold = float(model.get("risk_threshold", 0.65))
    return {
        "predicted_failure_probability": round(probability, 6),
        "risk_threshold": threshold,
        "risk_level": "ELEVATED" if probability >= threshold else "NORMAL",
        "model_version": model.get("model_version", "unversioned"),
    }
