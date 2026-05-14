import logging
import os

import redis
import requests
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from cache import get_weather_from_cache, save_weather_in_cache

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
WEATHER_API_KEY = os.getenv("VISUAL_CROSSING_API_KEY")
assert WEATHER_API_KEY is not None, "API key wasn't set in .env file"


@api_view(["GET"])
def root(request):
    return Response(data={"details": "hello, World"})


@api_view(["GET"])
@throttle_classes([AnonRateThrottle])
def get_weather(request, location: str):
    location = location.lower()
    # Try and get weather from cache, fallback to 3rd Party API if redis is unavailable
    try:
        weather_from_cache = get_weather_from_cache(location)
        if weather_from_cache:
            logger.info(f"{location} weather info retrieved from cache.")

            return Response(weather_from_cache)
    except redis.RedisError:
        logger.warning("Cache unavailable, using the API")

    logger.info(f"{location} weather info not found in cache, using API...")

    try:
        # Make a request to the api
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}"
        q_params = {"key": WEATHER_API_KEY}
        weather_response = requests.get(url, q_params, timeout=20)

        logger.info("request to API initiated")

        # Raises an HTTP error if status_code is 4XX or 5XX
        weather_response.raise_for_status()

        # save the response in a redis cache, return response without caching if redis is unavailable
        json_weather_response = weather_response.json()
        try:
            save_weather_in_cache(location, json_weather_response)
            logger.info(f"{location} weather info successfully cached")
        except redis.RedisError:
            logger.warning(
                f"Failed to cache {location} weather info, returning weather info without caching"
            )

        return Response(data=json_weather_response)

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code

        if status_code == 400:
            return Response(
                {"status": "error", "detail": "Invalid location parameter specified"},
                status=status_code,
            )

        if status_code == 401:
            return Response(
                {
                    "status": "error",
                    "detail": "Invalid API key",
                },
                status=status_code,
            )

        if status_code == 404:
            return Response(
                {
                    "status": "error",
                    "detail": "Endpoint for API request could not be found",
                },
                status=status_code,
            )

        if status_code >= 500:
            return Response(
                {"status": "error", "detail": "3rd Party API Error"},
                status=status_code,
            )

    except requests.exceptions.ConnectionError:
        return Response(
            {
                "status": "error",
                "detail": "No Internet connection detected. Please check your network settings and try again",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except requests.exceptions.Timeout:
        return Response(
            {
                "status": "error",
                "detail": "Request to external API timed out",
            },
        )
