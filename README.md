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
1. **hour**: hour of the day when the temperature will be considered to calculate coolness.  default value 14. range 0 to 23.
2. **size**: Length of the result set. How many districts will be returned. default value 10. range 1 to 64. 

Example curl command for the api.
```curl
curl --location 'localhost:8000/coolest?hour=14&size=10'
```