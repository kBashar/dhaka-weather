import json
from os import path

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
url = "https://api.open-meteo.com/v1/forecast"


def serialize_location_data():
	filepath = path.abspath(path.join(basepath, "..", "bd-districts.json"))
	with open(filepath, "r+") as districts_file:
		districts_json = json.load(districts_file)
		districts_list = districts_json["districts"]
		latitudes = []
		longitudes = []
		for dis in districts_list:
			latitudes.append(dis["lat"])
			longitudes.append(dis["long"])
		return latitudes, longitudes


def get_weather_data_for_district():
	latitudes, longitudes = serialize_location_data()
	params = {
		"latitude": latitudes,
		"longitude": longitudes,
		"hourly": "temperature_2m",
		"timezone": "Asia/Dhaka"
	}
	responses = openmeteo.weather_api(url, params=params)
	res = {
		"length": len(responses)
	}
	return res