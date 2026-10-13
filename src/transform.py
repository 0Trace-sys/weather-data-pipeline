from datetime import datetime, timezone


def transform_weather(weather_data):
    records = []

    times = weather_data["hourly"]["time"]
    temperatures = weather_data["hourly"]["temperature_2m"]

    if len(times) != len(temperatures):
        raise ValueError("Timestamp and temperature counts do not match")

    for timestamp, temperature in zip(times, temperatures):

        # Skip missing temperatures
        if temperature is None:
            continue

        # Validate the timestamp
        valid_timestamp = datetime.fromisoformat(timestamp).replace(
    tzinfo=timezone.utc
)

        # Convert temperature to a number
        temperature = float(temperature)

        # Build a structured weather record
        record = {
            "city": "Wichita Falls",
            "timestamp": valid_timestamp.isoformat(),
            "temperature_f": temperature
        }

        records.append(record)

    return records