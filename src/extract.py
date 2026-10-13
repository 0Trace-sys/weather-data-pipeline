import requests

# Open-Meteo API endpoint
url = "https://api.open-meteo.com/v1/forecast"

# Location and weather measurements
params = {
    "latitude": 33.9137,
    "longitude": -98.4934,
    "hourly": "temperature_2m",
    "temperature_unit": "fahrenheit",
    "timezone": "America/Chicago"
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
