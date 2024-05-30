from typing import Union

from fastapi import FastAPI, Query

from app.libs.openmeteo import (
    collect_weather_data_for_next_7_days,
    get_coolest_districts
)

collect_weather_data_for_next_7_days()

app = FastAPI()


@app.get("/coolest")
def get(
    hour: int = Query(default=14, le=23, ge=0),
    size: int = Query(default=10, le=64, ge=1)
):
    return get_coolest_districts(hour, size)

