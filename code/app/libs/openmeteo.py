import json
import logging
from os import path

import requests
import openmeteo_requests

import requests_cache
from retry_requests import retry

basepath = path.dirname(__file__)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
openmeteo_url = "https://api.open-meteo.com/v1/forecast"


def fetch_districts():
    try:
        response = requests.get("https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json")
        if response.status_code == 200:
            data = response.json()
            districts = data["districts"]
            return districts
    except Exception as e:
        logging.error(str(e))


def fetch_weather_data(latitudes, longitudes):
    payload = {
        "latitude": latitudes,
        "longitude": longitudes,
        "hourly": "temperature_2m"
    }
    try:
        response = requests.get(openmeteo_url, params=payload)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        logging.error("Weather data fetching from openmeteo failed.")
        return None


def save_weather_data(data):
    filepath = path.abspath(path.join(basepath, "..", "bd-districts-weather.json"))
    try:
        with open(filepath, "w+") as weather_file:
            json.dump(data, weather_file)
    except Exception:
        logging.error("Failed to save the weather data to disk.")


def collect_weather_data_for_next_7_days():
    districts = fetch_districts()

    if districts is None:
        logging.info("districts data fetching failed.")
        return None

    all_latitudes = []
    all_longitudes = []

    for dist in districts:
        all_latitudes.append(dist["lat"])
        all_longitudes.append(dist["long"])

    weather_data = fetch_weather_data(all_latitudes, all_longitudes)

    if weather_data is None:
        logging.info("weather data fetching failed")
        return None

    district_map = dict()
    for district, dist_weather_data in zip(districts, weather_data):
        district["weather"] = dist_weather_data

        # we store the district data mapped to their id, this will sped up the process later
        district_map[district["id"]] = district

    save_weather_data(district_map)

    return {
        "collected": True
    }
