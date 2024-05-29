from typing import Union

from fastapi import FastAPI

from app.libs.openmeteo import get_weather_data_for_district

app = FastAPI()


@app.get("/coolest")
def get_coolest_districts():
    return get_weather_data_for_district()
