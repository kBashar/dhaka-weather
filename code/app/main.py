import logging

import pytz
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from app.libs.openmeteo import collect_weather_data_for_cooling_calculation
from app.libs.weather_predictor import train_temperature_data_for_prediction
from app.router.endpoints import router

logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
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


app.include_router(router)
