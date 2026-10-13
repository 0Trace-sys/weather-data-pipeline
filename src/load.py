import psycopg


def load_weather(records):
    inserted_count = 0

    # Connect to the local PostgreSQL database
    with psycopg.connect(
        dbname="weather_pipeline",
        user="Cadmin",
        host="localhost"
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