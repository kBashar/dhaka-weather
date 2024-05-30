from typing import Union

from fastapi import FastAPI, Query

from app.libs.openmeteo import (
    collect_weather_data_for_next_7_days,
    get_coolest_districts
)

collect_weather_data_for_next_7_days()

app = FastAPI()

coolest_description = """
This api returns the coolest districts for next 7 days in ascending order of average temperatures in a given hour. As query parameter this api  endpoint 
takes two parameters.
| **Parameter** | **Description**                                                                                             | **Default Value** | **Range**   |
|---------------|-------------------------------------------------------------------------------------------------------------|-------------------|-------------|
| **hour**      | Hour of the day when the temperature will be considered to calculate coolness.                              | 14                | 0 to 23     |
| **size**      | Length of the result set. How many districts will be returned.                                              | 10                | 1 to 64     |
"""

@app.get("/coolest", description=coolest_description)
def get(
    hour: int = Query(default=14, le=23, ge=0),
    size: int = Query(default=10, le=64, ge=1)
):
    return get_coolest_districts(hour, size)

