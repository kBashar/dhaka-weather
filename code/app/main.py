from typing import Union

from fastapi import FastAPI

from app.libs.openmeteo import collect_weather_data_for_next_7_days

app = FastAPI()


@app.get("/coolest")
def get_coolest_districts():
    return collect_weather_data_for_next_7_days()
