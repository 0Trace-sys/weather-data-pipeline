
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

        result = transform_weather(data)

        self.assertEqual(len(result), 0)

    def test_invalid_timestamp(self):
        data = {
            "hourly": {
                "time": ["not-a-date"],
                "temperature_2m": [78.2]
            }
        }

        with self.assertRaises(ValueError):
            transform_weather(data)


if __name__ == "__main__":
    unittest.main()
