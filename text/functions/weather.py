import openmeteo_requests

import requests_cache
from retry_requests import retry
import requests

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def get_lat_long(location):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
    response = requests.get(url)
    response = response.json()
    return response["results"][0]["latitude"], response["results"][0]["longitude"]

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

def get_weather(location):
    lat, long = get_lat_long(location)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "cloud_cover",
            "pressure_msl",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ],
        "past_hours": 1,
        "forecast_days": 1,
        "forecast_hours": 1,
        "models": "best_match",
    }
    responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    
# Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    current_is_day = current.Variables(3).Value()
    current_precipitation = current.Variables(4).Value()
    current_rain = current.Variables(5).Value()
    current_showers = current.Variables(6).Value()
    current_snowfall = current.Variables(7).Value()
    current_cloud_cover = current.Variables(8).Value()
    current_pressure_msl = current.Variables(9).Value()
    current_surface_pressure = current.Variables(10).Value()
    current_wind_speed_10m = current.Variables(11).Value()
    current_wind_direction_10m = current.Variables(12).Value()
    current_wind_gusts_10m = current.Variables(13).Value()

    return {
        "Current time": current.Time(),
        "Current temperature_2m": current_temperature_2m,
        "Current relative_humidity_2m": current_relative_humidity_2m,
        "Current apparent_temperature": current_apparent_temperature,
        "Current is_day": "Day" if current_is_day else "Night",
        "Current precipitation": current_precipitation,
        "Current rain": current_rain,
        "Current showers": current_showers,
        "Current snowfall": current_snowfall,
        "Current cloud_cover": current_cloud_cover,
        "Current pressure_msl": current_pressure_msl,
        "Current surface_pressure": current_surface_pressure,
        "Current wind_speed_10m": current_wind_speed_10m,
        "Current wind_direction_10m": current_wind_direction_10m,
        "Current wind_gusts_10m": current_wind_gusts_10m,
    }


# print(f"Current time {current.Time()}")
# print(f"Current temperature_2m {current_temperature_2m}")
# print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
# print(f"Current apparent_temperature {current_apparent_temperature}")
# print(f"Current is_day {'Day' if current_is_day else 'Night'}")
# print(f"Current precipitation {current_precipitation}")
# print(f"Current rain {current_rain}")
# print(f"Current showers {current_showers}")
# print(f"Current snowfall {current_snowfall}")
# print(f"Current cloud_cover {current_cloud_cover}")
# print(f"Current pressure_msl {current_pressure_msl}")
# print(f"Current surface_pressure {current_surface_pressure}")
# print(f"Current wind_speed_10m {current_wind_speed_10m}")
# print(f"Current wind_direction_10m {current_wind_direction_10m}")
# print(f"Current wind_gusts_10m {current_wind_gusts_10m}") 

