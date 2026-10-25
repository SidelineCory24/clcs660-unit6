import unittest
from src.features import validate_features

VALID = {
    "cpu_mean": 88, "cpu_trend": 8, "memory_mean": 91,
    "error_rate": 0.07, "latency_p95_ms": 1800, "restart_count": 3,
}


class FeatureValidationTests(unittest.TestCase):
    def test_valid_features_keep_stable_order(self):
        values = validate_features(VALID)
        self.assertEqual(len(values), 6)
        self.assertEqual(values[0], 88.0)

    def test_missing_feature_is_rejected(self):
        sample = dict(VALID)
        del sample["cpu_mean"]
        with self.assertRaises(ValueError):
            validate_features(sample)

    def test_out_of_range_cpu_is_rejected(self):
        sample = dict(VALID, cpu_mean=120)
        with self.assertRaises(ValueError):
            validate_features(sample)

    def test_non_finite_value_is_rejected(self):
        sample = dict(VALID, cpu_trend=float("nan"))
        with self.assertRaises(ValueError):
            validate_features(sample)


if __name__ == "__main__":
    unittest.main()
