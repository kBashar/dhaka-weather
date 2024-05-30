from datetime import datetime

import pandas as pd
from prophet import Prophet

from app.libs.openmeteo import fetch_weather_data

model = Prophet()  # model initialization


def train_temperature_data_for_prediction():
    latitude = "23.7115253"
    longitude = "90.4111451"
    data = fetch_weather_data(latitude, longitude)

    if data:
        hourly_temperatures = data.get("hourly")
        print(hourly_temperatures["time"][0])
        df = pd.DataFrame(hourly_temperatures)
        df.rename(columns={'time': 'ds', 'temperature_2m': 'y'}, inplace=True)

        model.fit(df)   # fine tune the model


def predict_temperature(date: datetime):
    # date = pd.to_datetime(date_str)
    future = pd.DataFrame({'ds': [date]})

    # Make prediction
    forecast = model.predict(future)
    prediction = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[0]

    return {
        'date': prediction['ds'].strftime('%Y-%m-%d %H:%M:%S'),
        'predicted_temperature': round(prediction['yhat'], 2),
        'lower_bound': round(prediction['yhat_lower'], 2),
        'upper_bound': round(prediction['yhat_upper'], 2)
    }
