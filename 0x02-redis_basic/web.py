#!/usr/bin/env python3
"""Expiring web cache module"""


import redis
import requests
from functools import wraps

redis = redis.Redis()


def wrap_requests(method):
    """Wrapper decorator for get_page function"""
    @wraps(method)
    def wrapper(url):
        """wrapper decorator function"""
        key = "cached:" + url
        cached_response = redis.get(key)
        if cached_response:
            return cached_response.decode("utf-8")

            # Get new content and update cache
        key_count = "count:" + url
        response = method(url)

        redis.incr(key_count)
        redis.set(key, response, ex=10)
        redis.expire(key, 10)
        return response
    return wrapper


@wrap_requests
def get_page(url: str) -> str:
    """get_page"""
    results = requests.get(url)
    return results.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
