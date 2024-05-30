import logging
from datetime import datetime

import pandas as pd
from prophet import Prophet

from app.libs.openmeteo import fetch_weather_data

model = Prophet()  # model initialization


def train_temperature_data_for_prediction():
    """
    This function fetch weather data for Dhaka. Then use `hourly` data to create a
    pandas data-frame which then used to fit/fine-tune the `prophet` model.
    Finetuned model is saved in global `model` variable to be used later to predict weather.
    This function should be called to load/refresh new weather data.

    ### Parameters
    None

    ### Returns
    None
    """
    logging.info("Temperature model training started")
    latitude = "23.7115253"
    longitude = "90.4111451"
    data = fetch_weather_data(latitude, longitude)

    if data:
        hourly_temperatures = data.get("hourly")
        df = pd.DataFrame(hourly_temperatures)
        df.rename(columns={'time': 'ds', 'temperature_2m': 'y'}, inplace=True)

        model.fit(df)   # fine tune the model
    logging.info("Model training finished.")


def predict_temperature(date: datetime):
    """
    Predicts temperature for a given date.

    ### Parameter
    `date` - The future date for which we want to predict the temperature. 
            This takes python datetime object.
    """

    future = pd.DataFrame({'ds': [date]})

    forecast = model.predict(future)
    prediction = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[0]

    return {
        'date': prediction['ds'].strftime('%Y-%m-%d %H:%M:%S'),
        'predicted_temperature': round(prediction['yhat'], 2),
        'lower_bound': round(prediction['yhat_lower'], 2),
        'upper_bound': round(prediction['yhat_upper'], 2)
    }
