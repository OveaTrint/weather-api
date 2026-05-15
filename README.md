# Weather API Project
A weather API built using the [Django Rest Framework](https://www.django-rest-framework.org/) that implements caching using
[redis](https://redis.io/)

Project Idea gotten from [roadmap.sh](https://roadmap.sh/projects/weather-api-wrapper-service)

## How it works
It uses a 3rd party API weather service called [Visual Crossing](https://www.visualcrossing.com/) to get weather details.
It needs an API key which you can get from the link above.

Caching is implemented using redis which is a key-value NoSQL database. You can learn how to set it up and get it running on your machine from [here](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/)

It uses the `/get_weather` endpoint with the `location` as the input required from the user to get the weather details

## How to Run
Clone the repo
```bash
git clone https://github.com/OveaTrint/weather-api.git
```
Change the current working directory to the project
```bash 
cd weather-api
```

Sync the dependencies
```bash
uv sync
```

Run the server
```bash
python manage.py runserver
```

Then go to localhost:8000 and test the "/get_weather" endpoint to get your weather details
