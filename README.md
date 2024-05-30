# Backend Developer with AI Focus Assignment

## Features

1. Endpoint to get on average coolest districts per hour basis based on next 7 days data.  
2. Predict Dhaka's temperature for future date and time.  
3. Refresh temperature data every 24 hours with corn job.  
4. Extensive documentation of process and performance.  
5. Easy installation and setup with docker.  

## Run the app  

1. Clone this repository
2. Move to the `code` directory i.e. 
```shell
   cd code
```
3. To build and run the app with docker run following docker compose command.
```shell
    docker compose up -build
```
This will download required docker images and other project dependencies.
4. Visit to [http://localhost:8000/docs](http://localhost:8000/docs) to access the API documentation and swagger.


## About Endpoints 

### `/coolest` 
This api returns the coolest districts for next 7 days in ascending order of average temperatures in a given hour. As query parameter this api  endpoint 
takes two parameters.
| **Parameter** | **Description**                                                                                             | **Default Value** | **Range**   |
|---------------|-------------------------------------------------------------------------------------------------------------|-------------------|-------------|
| **hour**      | Hour of the day when the temperature will be considered to calculate coolness.                              | 14                | 0 to 23     |
| **size**      | Length of the result set. How many districts will be returned. |10                | 1 to 64     |

**Example curl command**
```curl
curl --location 'localhost:8000/coolest?hour=14&size=10'
```

**Response body**
```json
    [
        {
            "id": "54",
            "division_id": "7",
            "name": "Sylhet",
            "bn_name": "সিলেট",
            "lat": "24.8897956",
            "long": "91.8697894",
            "average_temperature": 26.67
        },
        ...
    ]
```

### `/predict`

Predicts temperature of a future date. Date should be today + 6 days.
| **Parameter** | **Description**                                                                                             |
|---------------|-------------------------------------------------------------------------------------------------------------|
| **date**      | Date for which the temperature prediction should be made. Date should in ISO8601                                           |

**Example curl command**
```curl
curl --location 'localhost:8000/predict?date=2024-06-10T12%3A00'
```

**Response body**
```json
    {
        "date": "2024-06-10 12:00:00",
        "predicted_temperature": 31.32,
        "lower_bound": 30.39,
        "upper_bound": 32.3
    }
```
## How It Works  

### Coolest Districts  
Coolest district calculation processing happens in several steps:

**Step-1**: Fetch all districts data, we keep it a network call to avoid stale data in case data related to a districts changes, though it is a rare event.  
**Step-2**: Make two lists, one containing latitudes and another longitudes of the districts.  
**Step-3**: Fetch weather data for coming 7 days using openmeteo.  
**Step-4**: Calculate average temperature for each hour of every districts.  
**Step-5**: Save the calculated data for future use.  
**Step-6**: Serve the pre-calculated data through `/coolest` api endpoint.  

### Temperature Prediction
We used prophet time series model to fine tune for our temperature prediction purpose.
Temperature prediction happens in following steps:  

**Step-1**: This function fetch weather data for Dhaka.  
**Step-2**: Then use `hourly` data to create a pandas data-frame which then used to fit/fine-tune the `prophet` model.  
**Step-3**: Fine-tuned model is saved in global `model` variable to be used later to predict weather.  
**Step-4**: Use the saved model to predict temperature for future dates.   

## Performance

### `/coolest` 

As we save the collected and processed data in runtime memory, response time is well below constrained 500ms.  
Following chart will bear truth to the above claim. We notice initial request takes more time and as time progress response time stabilize to 3ms.

|   hour |   size |   response_time |
|-------:|-------:|----------------:|
|     14 |     10 |              12 |
|      0 |      4 |               4 |
|      0 |     64 |               7 |
|      9 |     20 |               3 |
|     10 |      5 |               3 |


### `/predict` 

Models performs better when future date is nearer to the training date and
slips away further as we go further the time. This can be improved with more training data.
Here we are fitting the model with only 7 days of temperature data.

| Date                | Distance | Predicted |
|---------------------|----------|-----------|
| 2024-06-10 12:00:00 | 10 days  | 28.96     |
| 2024-07-10 12:00:00 | 40 days  | 24.07     |
| 2025-07-10 12:00:00 | 375 days | -35.39    |
