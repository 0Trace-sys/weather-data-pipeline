import requests
from transform import transform_weather
from load import load_weather
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

# Request weather data from the API
response = requests.get(url, params=params, timeout=10)

# Raise an error if the request failed
response.raise_for_status()

# Convert JSON into a Python dictionary
weather_data = response.json()

# Print the first five observations
print("First five timestamps:")
print(weather_data["hourly"]["time"][:5])

print("First five temperatures:")
print(weather_data["hourly"]["temperature_2m"][:5])

# Transform the extracted weather data
clean_records = transform_weather(weather_data)

print("\nFirst five transformed records:")

for record in clean_records[:5]:
    print(record)

# Load the transformed weather data into the database
inserted_count = load_weather(clean_records)
print(f"\nInserted {inserted_count} new records into the database.")