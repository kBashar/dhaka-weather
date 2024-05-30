# strativ-test
Backend Developer with AI Focus Assignment


## Run the app  

1. Clone this repository
2. Move to the `code` directory i.e. 
```shell
   cd code
```
3. To build and run the app with docker run following docker compose command.
This will download required docker images and other project dependencies.
```shell
    docker compose up -build
```
4. Visit to [http://localhost:8000/docs](http://localhost:8000/docs) to access the documentation.


## API Documentation  

### `/coolest` 
This api returns the coolest districts for next 7 days in ascending order of average temperatures in a given hour. As query parameter this api  endpoint 
takes two parameters.
| **Parameter** | **Description**                                                                                             | **Default Value** | **Range**   |
|---------------|-------------------------------------------------------------------------------------------------------------|-------------------|-------------|
| **hour**      | Hour of the day when the temperature will be considered to calculate coolness.                              | 14                | 0 to 23     |
| **size**      | Length of the result set. How many districts will be returned. |10                | 1 to 64     |

Example curl command for the api.
```curl
curl --location 'localhost:8000/coolest?hour=14&size=10'
```

### `/predict`

Predicts temperature of a future date. Date should be today + 6 days.
| **Parameter** | **Description**                                                                                             |
|---------------|-------------------------------------------------------------------------------------------------------------|
| **date**      | Date for which the temperature prediction should be made. Date should                                                   |

Example curl command for the api.
```curl
curl --location 'localhost:8000/predict?date=2024-06-10T12%3A00'
```