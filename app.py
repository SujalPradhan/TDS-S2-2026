import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup session with caching + retry
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Open-Meteo endpoint
url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 29.0588,      # Example: Delhi
    "longitude": 76.0856,
    "current": [
        "temperature_2m",
        # "relative_humidity_2m",
        # "precipitation"
    ]
}

responses = openmeteo.weather_api(url, params=params)
response = responses[0]

current = response.Current()

temperature = current.Variables(0).Value()
# humidity = current.Variables(1).Value()
# precipitation = current.Variables(2).Value()

print("Current Weather:")
print(f"Temperature: {temperature} °C")
# print(f"Humidity: {humidity} %")
# print(f"Precipitation: {precipitation} mm")