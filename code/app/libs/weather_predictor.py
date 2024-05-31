import logging
from datetime import datetime, date

import pandas as pd
from prophet import Prophet

from app.libs.openmeteo import fetch_weather_data

model = Prophet()  # model initialization

def get_day_average_temperature(times, temperatures):
    
    average_temp = sum(temperatures)/len(temperatures)
    date = datetime.strptime(times[0], "%y-%m-%dT%H:%M").date()

    return date, average_temp


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
        times = hourly_temperatures["time"]
        temperatures = hourly_temperatures["temperature_2m"]

        daily_temperatures = {
            "date": [],
            "avg_temperature": []
        }
        for i in range(0, len(temperatures), 24):
            average_temp = sum(temperatures[i:i+24])/24
            date = datetime.strptime(times[i], "%Y-%m-%dT%H:%M").date()
            daily_temperatures["date"].append(date)
            daily_temperatures["avg_temperature"].append(average_temp)

        df = pd.DataFrame(daily_temperatures)
        df.rename(columns={"date": "ds", "avg_temperature": "y"}, inplace=True)

        model.fit(df)   # fine tune the model
        logging.info("Model training finished.")


def predict_temperature(date: date):
    """
    Predicts temperature for a given date.

    ### Parameter
    `date` - The future date for which we want to predict the temperature. 
            This takes python datetime object.
    """

    future = pd.DataFrame({"ds": [date]})

    forecast = model.predict(future)
    prediction = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].iloc[0]

    return {
        "date": prediction["ds"].strftime("%Y-%m-%d"),
        "predicted_avg_temperature": round(prediction["yhat"], 2),
        "lower_bound": round(prediction["yhat_lower"], 2),
        "upper_bound": round(prediction["yhat_upper"], 2)
    }
