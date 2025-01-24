import time
from functools import wraps
from logging import Logger
from typing import Type

from .exception import exception_msg


def singleton(cls):
    """Singleton decorator
    """
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


def retry(attempts: int = 2,
          wait_time: int = 1,
          on_exceptions: set[Type[Exception]] | None = None,
          logger: Logger | None = None):
    """Retry decorator

    Args:
        attempts (int, optional): the maximum number of retries. Defaults to 2 attempts in total
        wait_time (int, optional): how long to wait before retrying. Defaults to 0 for immediate retry
        on_exceptions (set[Type[Exception]] | None, optional): the exceptions for which the function should be retried. Defaults to None
        logger (Logger | None, optional): Logger
    """
    # In case if invalid `attempts` is provided
    if attempts < 1:
        attempts = 1

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if on_exceptions and type(e) not in on_exceptions:
                        # If unexpected exception caught, throw directly as it's not in the retry list
                        if logger:
                            logger.error(
                                f'Attempt {attempt}: unexpected exception caught for function {func}, error: {exception_msg(e)}')
                        raise e

                    if attempt < attempts:
                        if logger:
                            logger.warning(
                                f'Attempt {attempt}: failed to execute function {func}, wait for retry, error: {exception_msg(e)}')
                        time.sleep(wait_time)
                    else:
                        if logger:
                            logger.error(
                                f'Attempt {attempt}: failed to execute function {func} with final attempt, error: {exception_msg(e)}')
                        raise e
        return wrapper
    return decorator


def log_error(logger: Logger, prefix: str | None = None):
    """Log error decorator

    Args:
        logger (Logger): Logger
        prefix (str | None, optional): The prefix to be added to the error message. Defaults to None
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if prefix:
                    logger.error(f'{prefix}: {exception_msg(e)}')
                else:
                    logger.error(exception_msg(e))
                return None

        return wrapper
    return decorator
