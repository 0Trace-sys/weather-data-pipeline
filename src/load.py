
import os
import psycopg
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def load_weather(records):
    affected_count = 0

    # Connect to PostgreSQL
    with psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    ) as conn:

        # Create a database cursor
        with conn.cursor() as cur:

            for record in records:
                cur.execute(
                    """
                    INSERT INTO weather_forecasts
                        (city, forecast_time, temperature_f)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (city, forecast_time)
                    DO UPDATE SET
                        temperature_f = EXCLUDED.temperature_f,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE weather_forecasts.temperature_f
                        IS DISTINCT FROM EXCLUDED.temperature_f
                    """,
                    (
                        record["city"],
                        record["timestamp"],
                        record["temperature_f"]
                    )
                )

                affected_count += cur.rowcount

    return affected_count
