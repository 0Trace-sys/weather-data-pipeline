import os
import psycopg
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def load_weather(records):
    inserted_count = 0

    # Connect to the local PostgreSQL database
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
                    INSERT INTO weather_observations
                        (city, observation_time, temperature_f)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (city, observation_time)
                    DO NOTHING
                    """,
                    (
                        record["city"],
                        record["timestamp"],
                        record["temperature_f"]
                    )
                )

                inserted_count += cur.rowcount

    return inserted_count