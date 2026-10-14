"""Optional checks against PostgreSQL; set WEATHER_TEST_DSN to enable."""

import importlib
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
TEST_DSN = os.getenv("WEATHER_TEST_DSN")


@unittest.skipUnless(TEST_DSN, "Set WEATHER_TEST_DSN to a dedicated test database")
class TestWeatherLoadIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        from psycopg import sql

        cls.psycopg = psycopg
        cls.sql = sql
        cls.connect_db = staticmethod(psycopg.connect)
        cls.schema = "weather_test_" + uuid4().hex
        # Do not import connection settings from a developer's .env file.
        with patch.dict(os.environ, {"PYTHON_DOTENV_DISABLED": "1"}):
            cls.loader = importlib.import_module("load")
        with cls.connect_db(TEST_DSN) as conn:
            conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(cls.schema)))
        cls.addClassCleanup(cls.drop_schema)
        with cls.connection() as conn:
            conn.execute((ROOT / "sql/schema.sql").read_text())

    @classmethod
    def connection(cls):
        return cls.connect_db(TEST_DSN, options=f"-c search_path={cls.schema}")

    @classmethod
    def drop_schema(cls):
        with cls.connect_db(TEST_DSN) as conn:
            conn.execute(cls.sql.SQL("DROP SCHEMA {} CASCADE").format(
                cls.sql.Identifier(cls.schema)
            ))

    def setUp(self):
        with self.connection() as conn:
            conn.execute("TRUNCATE weather_forecasts")
        # Exercise the real loader SQL and transactions in this test schema.
        self.connect_patch = patch.object(
            self.loader.psycopg, "connect",
            side_effect=lambda *args, **kwargs: self.connection()
        )
        self.connect_patch.start()
        self.addCleanup(self.connect_patch.stop)
        self.records = [
            {"city": "Wichita Falls", "timestamp": "2026-10-14T00:00:00+00:00",
             "temperature_f": 70.0},
            {"city": "Wichita Falls", "timestamp": "2026-10-14T01:00:00+00:00",
             "temperature_f": 72.0}
        ]

    def rows(self):
        with self.connection() as conn:
            return conn.execute(
                "SELECT city, forecast_time, temperature_f, created_at, updated_at "
                "FROM weather_forecasts ORDER BY forecast_time"
            ).fetchall()

    def test_insert_and_unchanged_rerun(self):
        self.assertEqual(self.loader.load_weather(self.records), 2)
        before = self.rows()
        self.assertEqual(len(before), 2)
        self.assertEqual(self.loader.load_weather(self.records), 0)
        self.assertEqual(self.rows(), before)

    def test_changed_forecast_updates_existing_row(self):
        self.loader.load_weather(self.records)
        with self.connection() as conn:
            conn.execute("UPDATE weather_forecasts SET updated_at = '2000-01-01Z'")
        before = self.rows()
        self.records[0]["temperature_f"] = 71.0
        self.assertEqual(self.loader.load_weather(self.records), 1)
        after = self.rows()
        self.assertEqual(len(after), 2)
        self.assertEqual(after[0][2], 71.0)
        self.assertEqual(after[0][3], before[0][3])
        self.assertGreater(after[0][4], before[0][4])
        self.assertEqual(after[1], before[1])

    def test_failed_batch_rolls_back_earlier_update(self):
        self.loader.load_weather(self.records)
        before = self.rows()
        batch = [dict(self.records[0], temperature_f=99.0),
                 dict(self.records[1], city="x" * 101)]
        with self.assertRaises(self.psycopg.errors.StringDataRightTruncation):
            self.loader.load_weather(batch)
        self.assertEqual(self.rows(), before)

    def test_daily_summary_reports_partial_day_coverage(self):
        start = datetime(2026, 10, 14, tzinfo=timezone.utc)
        records = [
            {"city": "Wichita Falls",
             "timestamp": (start + timedelta(hours=hour)).isoformat(),
             "temperature_f": 70.0}
            for hour in range(168)
        ]
        self.loader.load_weather(records)
        with self.connection() as conn:
            queries = (ROOT / "sql/analysis.sql").read_text().split(";")
            # Execute the actual analysis file, including its daily summary.
            results = []
            for query in queries:
                if query.strip():
                    cursor = conn.execute(query)
                    results.append((
                        [column.name for column in cursor.description], cursor.fetchall()
                    ))
        columns, daily = results[-1]
        count_index = columns.index("hours_available")
        self.assertEqual([row[count_index] for row in daily], [5] + [24] * 6 + [19])
        self.assertEqual(sum(row[count_index] for row in daily), 168)


if __name__ == "__main__":
    unittest.main()
