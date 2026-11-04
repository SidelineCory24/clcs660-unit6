"""Feature validation and ordering shared by training and inference."""

# Order matters: model coefficients and scaler parameters are exported in this order.
FEATURE_NAMES = [
    "cpu_mean",
    "cpu_trend",
    "memory_mean",
    "error_rate",
    "latency_p95_ms",
    "restart_count",
]


def validate_features(record):
    """Return feature values in stable model order; reject missing/invalid input."""
    values = []
    # Pass 1: presence, type, and finiteness for every feature, in model order.
    for name in FEATURE_NAMES:
        if name not in record:
            raise ValueError(f"Missing required feature: {name}")
        try:
            value = float(record[name])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Feature {name} must be numeric") from exc
        # float() accepts "nan" and "inf"; neither is a meaningful measurement.
        if not __import__("math").isfinite(value):
            raise ValueError(f"Feature {name} must be finite")
        values.append(value)

    # Pass 2: range checks. Indexes follow FEATURE_NAMES order:
    # 0 cpu_mean, 2 memory_mean (percent), 3 error_rate (fraction), 4 latency_p95_ms, 5 restart_count.
    # cpu_trend (index 1) is a signed change, so it is intentionally unbounded.
    if not 0 <= values[0] <= 100:
        raise ValueError("cpu_mean must be between 0 and 100")
    if not 0 <= values[2] <= 100:
        raise ValueError("memory_mean must be between 0 and 100")
    if not 0 <= values[3] <= 1:
        raise ValueError("error_rate must be between 0 and 1")
    if values[4] < 0 or values[5] < 0:
        raise ValueError("latency_p95_ms and restart_count cannot be negative")
    return values
