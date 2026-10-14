
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from transform import transform_weather


class TestWeatherTransform(unittest.TestCase):

    def test_valid_weather_data(self):
        data = {
            "hourly": {
                "time": ["2026-10-13T00:00"],
                "temperature_2m": [78.2]
            }
        }

        result = transform_weather(data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["city"], "Wichita Falls")
        self.assertEqual(result[0]["temperature_f"], 78.2)
        self.assertEqual(
            result[0]["timestamp"],
            "2026-10-13T00:00:00+00:00"
        )

    def test_missing_temperature(self):
        data = {
            "hourly": {
                "time": ["2026-10-13T00:00"],
                "temperature_2m": [None]
            }
        }

        with self.assertRaisesRegex(ValueError, "No usable weather records"):
            transform_weather(data)

    def test_invalid_timestamp(self):
        data = {
            "hourly": {
                "time": ["not-a-date"],
                "temperature_2m": [78.2]
            }
        }

        with self.assertRaises(ValueError):
            transform_weather(data)

    def test_empty_forecast(self):
        data = {"hourly": {"time": [], "temperature_2m": []}}
        with self.assertRaisesRegex(ValueError, "No usable weather records"):
            transform_weather(data)

    def test_missing_temperature_keeps_valid_records(self):
        data = {"hourly": {
            "time": ["2026-10-13T00:00", "2026-10-13T01:00"],
            "temperature_2m": [None, 0]
        }}
        result = transform_weather(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["temperature_f"], 0.0)
        self.assertEqual(result[0]["timestamp"], "2026-10-13T01:00:00+00:00")

    def test_non_finite_temperatures(self):
        for value in [float("nan"), float("inf"), float("-inf"),
                      "NaN", "Infinity", "-Infinity", "1e309"]:
            with self.subTest(value=value):
                data = {"hourly": {
                    "time": ["2026-10-13T00:00", "2026-10-13T01:00"],
                    "temperature_2m": [78.2, value]
                }}
                with self.assertRaisesRegex(ValueError, "Temperature must be finite"):
                    transform_weather(data)

    def test_mismatched_counts(self):
        data = {"hourly": {
            "time": ["2026-10-13T00:00"], "temperature_2m": []
        }}
        with self.assertRaisesRegex(ValueError, "counts do not match"):
            transform_weather(data)


if __name__ == "__main__":
    unittest.main()
