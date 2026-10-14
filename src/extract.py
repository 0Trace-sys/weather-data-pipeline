import logging
import sys
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from transform import transform_weather
from load import load_weather


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    logging.info("Starting weather data pipeline")

    try:
        # Open-Meteo API endpoint
        url = "https://api.open-meteo.com/v1/forecast"

        # Location and weather measurements
        params = {
            "latitude": 33.9137,
            "longitude": -98.4934,
            "hourly": "temperature_2m",
            "temperature_unit": "fahrenheit",
            "timezone": "GMT"
        }

        # Configure automatic retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        # Extract weather data
        with requests.Session() as session:
            session.mount("https://", adapter)

            response = session.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()
            weather_data = response.json()

        logging.info(
            "Extracted %d weather records from Open-Meteo",
            len(weather_data["hourly"]["time"])
        )

        # Transform weather data
        clean_records = transform_weather(weather_data)

        logging.info(
            "Successfully transformed %d weather records",
            len(clean_records)
        )

        
        # Load weather data into PostgreSQL
        affected_count = load_weather(clean_records)

        logging.info(
            "Inserted or updated %d weather records in PostgreSQL",
            affected_count
        )

        logging.info("Weather data pipeline completed successfully")

    except Exception:
        logging.exception("Weather data pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

