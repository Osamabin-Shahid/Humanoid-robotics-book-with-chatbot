"""
Retry utilities for handling API failures gracefully.
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Any


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        backoff_factor: Factor by which delay increases after each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Last attempt, raise the exception
                        logging.error(f"Function {func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise e

                    # Calculate delay with exponential backoff
                    delay = base_delay * (backoff_factor ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                                  f"Retrying in {delay:.2f} seconds...")

                    time.sleep(delay)

            # This should never be reached, but added for type checking
            raise last_exception

        return wrapper
    return decorator


def rate_limit(calls_per_second: float = 1.0):
    """
    Decorator to limit the rate of function calls.

    Args:
        calls_per_second: Maximum number of calls allowed per second
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret

        return wrapper
    return decorator


class RetryHandler:
    """
    A class to handle retry logic for API calls.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """
        Initialize the retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            backoff_factor: Factor by which delay increases after each retry
            exceptions: Tuple of exceptions to catch and retry on
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function call
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e

                if attempt == self.max_retries:
                    # Last attempt, raise the exception
                    logging.error(f"Function failed after {self.max_retries} retries: {str(e)}")
                    raise e

                # Calculate delay with exponential backoff
                delay = self.base_delay * (self.backoff_factor ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. "
                              f"Retrying in {delay:.2f} seconds...")

                time.sleep(delay)

        # This should never be reached
        raise last_exception