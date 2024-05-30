import json
import logging
from os import path

import requests

basepath = path.dirname(__file__)

latest_weather_data = None


def fetch_districts():
    """
    Data fetcher for districts. Fetch all districts data, we keep it a network call to avoid stale data 
    in case data related to a districts changes, though it is a rare event.

    ### Returns
    json response received from github.
    """
    try:
        response = requests.get("https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json")
        if response.status_code == 200:
            data = response.json()
            districts = data["districts"]
            return districts
    except Exception as e:
        logging.error(str(e))


def fetch_weather_data(latitudes, longitudes, forecast_days: int = 7):
    """
    Data fetcher for district temperatures. By default it takes 7 days of forecast.

    ### Returns
    json response received from openmeteo.
    """
    payload = {
        "latitude": latitudes,
        "longitude": longitudes,
        "hourly": "temperature_2m",
        "forecast_days": forecast_days
    }
    try:
        openmeteo_url = "https://api.open-meteo.com/v1/forecast"
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
    """
    Data Collector function, it collects data in following steps

    Step-1: Fetch all districts data, we keep it a network call to avoid stale data 
            in case data related to a districts changes, though it is a rare event.
    Step-2: Make two lists, one containing latitudes and another longitudes of the districts.
    Step-3: Fetch weather data for coming 7 days using openmeteo
    Step-4: Calculate average temperature for each hour of every districts.
    Step-5: Save the calculated data for future use.
    """

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


def get_coolest_districts(hour=14, size=10):
    """
    returns a list of districts that are most coolest aka has least temperature among all districts.

    ### parameter
    `hour`: Interested hour of the day. It takes hour in 0-23 and default is 14 aka 2PM.
    `size`: Number of districts to return. It takes 1-64 and by default it returns 10 districts 
            sorted in their temperatures ascending order.
    """
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

