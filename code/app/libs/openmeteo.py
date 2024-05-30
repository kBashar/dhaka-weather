import json
import logging
from os import path

import requests

basepath = path.dirname(__file__)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
openmeteo_url = "https://api.open-meteo.com/v1/forecast"

latest_weather_data = None
coolest_weather_data = {}


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
        "hourly": "temperature_2m",
        "forecast_days": 7
    }
    try:
        response = requests.get(openmeteo_url, params=payload)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        logging.error(str(e))
        return None


def save_weather_data(data):
    global latest_weather_data
    filepath = path.abspath(path.join(basepath, "..", "bd-districts-weather.json"))
    try:
        with open(filepath, "w+") as weather_file:
            json.dump(data, weather_file)
            latest_weather_data = data
    except Exception:
        logging.error("Failed to save the weather data to disk.")


def load_weather_data():
    global latest_weather_data
    filepath = path.abspath(path.join(basepath, "..", "bd-districts-weather.json"))
    try:
        with open(filepath, "r+") as weather_file:
            latest_weather_data = json.load(weather_file)
    except Exception:
        logging.error("Failed to save the weather data to disk.")


def collect_weather_data_for_cooling_calculation():
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
        logging.error("Weather data fetching from openmeteo failed.")
        return None

    for district, dist_weather_data in zip(districts, weather_data):
        hourly_temperatures = dist_weather_data["hourly"]["temperature_2m"]
        average_temperatures = dict()
        for hour in range(24):
            hour_temperatures = [temp for temp in hourly_temperatures[hour::24]]
            average_temp = sum(hour_temperatures)/len(hour_temperatures)
            average_temperatures[hour] = round(average_temp, 2)
        district["average_temperatures"] = average_temperatures
    save_weather_data(districts)

    return {
        "collected": True
    }


def get_coolest_districts(hour=14, size=10):
    if latest_weather_data is None:
        load_weather_data()
    sorted_districts = sorted(latest_weather_data, key=lambda x: x["average_temperatures"][hour])
    coolest_districts = sorted_districts[:size]
    new_list = []
    for obj in coolest_districts:
        o = {key: value for key, value in obj.items() if key != "average_temperatures"}
        o["average_temperature"] = obj["average_temperatures"][hour]
        new_list.append(o)
    return new_list

