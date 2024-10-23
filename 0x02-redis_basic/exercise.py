#!/usr/bin/env python3
"""Redis module"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Counts how many times methods 
    of the class cache are called"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Decorated function wrapper"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """history of inputs and outputs store"""
    inp = method.__qualname__ + ":inputs"
    out = method.__qualname__ + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Decorated function wrapper"""
        self._redis.rpush(inp, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(out, str(res))
        return res

    return wrapper


def replay(method: Callable) -> None:
    """Displays history of a particular function"""
    input_keys = "{}:inputs".format(method.__qualname__)
    output_keys = "{}:outputs".format(method.__qualname__)

    inputs = method.__self__._redis.lrange(inputs_key, 0, -1)
    outputs = method.__self__._redis.lrange(outputs_key, 0, -1)

    print("{} was called {} times:".format(method.__qualname__, len(inputs)))
    for inp, out in zip(inputs, outputs):
        print(
            "{}(*{}) -> {}".format(
                method.__qualname__, inp.decode("utf-8"), out.decode("utf-8")
            )
        )


class Cache:
    """Cache Redis Class"""

    def __init__(self):
        """Stores an instance of the Redis client"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Generates a random key"""
        keys = str(uuid.uuid4())
        self._redis.set(keys, data)
        return keys

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float]:
        """Converts the data back to the desired format"""
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Gets a string"""
        return self.get(key, fn=str)

    def get_int(self, key: str) -> int:
        """Gets a number"""
        return self.get(key, fn=int)
