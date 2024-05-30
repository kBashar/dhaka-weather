import logging
from datetime import datetime, timedelta

import pytz
from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from app.libs.openmeteo import (
    collect_weather_data_for_cooling_calculation,
    get_coolest_districts
)
from app.libs.weather_predictor import (
    predict_temperature,
    train_temperature_data_for_prediction
)

logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Format of the log messages
    handlers=[
        logging.StreamHandler()  # Console handler
    ]
)

app = FastAPI()
scheduler = BackgroundScheduler()


@app.on_event("startup")
async def startup_event():
    collect_weather_data_for_cooling_calculation()
    train_temperature_data_for_prediction()

    dhaka_tz = pytz.timezone('Asia/Dhaka')
    # add scheduler to reload data every day at 00:00 hour
    scheduler.add_job(collect_weather_data_for_cooling_calculation, 'cron', hour=00, minute=00, timezone=dhaka_tz)
    scheduler.add_job(train_temperature_data_for_prediction, 'cron', hour=00, minute=00, timezone=dhaka_tz)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


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
    response = get_coolest_districts(hour, size)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


predict_description = """
Predicts temperature of a future date. Date should be today + 6 days.
| **Parameter** | **Description**                                                                                             |
|---------------|-------------------------------------------------------------------------------------------------------------|
| **date**      | Date for which the temperature prediction should be made. Date should in ISO8601 format.                                                  |
"""


@app.get("/predict", description=predict_description)
def predict(
    date: datetime
):
    last_date_of_training = datetime.today() + timedelta(days=6)

    if date <= last_date_of_training:
        response = {
            "error": "Bad request",
            "message": f"Date should be in future of {last_date_of_training.strftime('%y-%m-%d')}"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response)

    response = predict_temperature(date)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)
