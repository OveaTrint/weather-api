import json
from typing import Any

import redis
from redis.cache import CacheConfig

EXPIRY_TIME_IN_SECONDS = 7200

r = redis.Redis(host="localhost", port=6379, cache_config=CacheConfig(), protocol=3)


def get_weather_from_cache(key: str) -> dict[str, Any] | None:
    cached_weather = r.get(key)

    if cached_weather is None:
        return cached_weather

    weather = json.loads(cached_weather)
    return weather


def save_weather_in_cache(key: str, value: dict[str, Any]) -> None:
    json_weather = json.dumps(value)
    r.set(key, json_weather, ex=EXPIRY_TIME_IN_SECONDS)
