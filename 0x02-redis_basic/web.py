#!/usr/bin/env python3
"""Expiring web cache module"""


import redis
import requests
from functools import wraps

r = redis.Redis()


def wrap_requests(method):
    """Wrapper decorator for get_page function"""
    @wraps(method)
    def wrapper(url):
        """wrapper decorator function"""
        key = "cached:" + url
        cached_value = r.get(key)
        if cached_value:
            return cached_value.decode("utf-8")

            # Get new content and update cache
        key_count = "count:" + url
        html_content = method(url)

        r.incr(key_count)
        r.set(key, html_content, ex=10)
        r.expire(key, 10)
        return html_content
    return wrapper


@wrapper_requests
def get_page(url: str) -> str:
    """get_page"""
    results = requests.get(url)
    return results.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
