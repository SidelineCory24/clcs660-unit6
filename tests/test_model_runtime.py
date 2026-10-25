import unittest
from src.model_runtime import predict_failure_risk

MODEL = {
    "model_version": "test",
    "scaler_mean": [50, 0, 50, 0.01, 200, 0],
    "scaler_scale": [10, 1, 10, 0.01, 100, 1],
    "coefficients": [1.5, 0.8, 1.2, 1.0, 0.8, 0.5],
    "intercept": -1.0,
    "risk_threshold": 0.65,
}
HIGH_RISK = {
    "cpu_mean": 90, "cpu_trend": 8, "memory_mean": 90,
    "error_rate": 0.08, "latency_p95_ms": 1500, "restart_count": 3,
}
LOW_RISK = {
    "cpu_mean": 25, "cpu_trend": -1, "memory_mean": 30,
    "error_rate": 0.001, "latency_p95_ms": 100, "restart_count": 0,
}


class ModelRuntimeTests(unittest.TestCase):
    def test_probability_is_bounded(self):
        result = predict_failure_risk(HIGH_RISK, MODEL)
        self.assertGreaterEqual(result["predicted_failure_probability"], 0)
        self.assertLessEqual(result["predicted_failure_probability"], 1)

    def test_high_risk_sample_flags_elevated(self):
        result = predict_failure_risk(HIGH_RISK, MODEL)
        self.assertEqual(result["risk_level"], "ELEVATED")

    def test_low_risk_sample_is_normal(self):
        result = predict_failure_risk(LOW_RISK, MODEL)
        self.assertEqual(result["risk_level"], "NORMAL")

    def test_model_version_is_returned(self):
        self.assertEqual(predict_failure_risk(LOW_RISK, MODEL)["model_version"], "test")


if __name__ == "__main__":
    unittest.main()
