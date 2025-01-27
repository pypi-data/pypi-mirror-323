import time
from functools import wraps
from loguru import logger


def timed_call(logger_instance):
    if logger_instance is None:
        logger_instance = logger.getLogger(__name__)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger_instance.info(f"{func.__name__} took {duration:.2f} seconds")
            return result

        return wrapper

    return decorator
