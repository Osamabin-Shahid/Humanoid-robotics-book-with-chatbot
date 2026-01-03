"""
Retry Utilities Module

This module provides utility functions for implementing retry logic with exponential backoff
for API calls and other operations that may fail temporarily.
"""
import time
import random
import logging
from functools import wraps
from typing import Callable, Type, Any, Optional


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    allowed_exceptions: Optional[tuple] = None
):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which delay increases after each retry
        jitter: Whether to add random jitter to delay times
        allowed_exceptions: Tuple of exceptions that trigger a retry
    """
    if allowed_exceptions is None:
        allowed_exceptions = (Exception,)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Final attempt - raise the exception
                        logging.warning(
                            f"Function {func.__name__} failed after {max_retries} retries. "
                            f"Last error: {type(e).__name__}: {str(e)}"
                        )
                        raise e

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                    if jitter:
                        # Add jitter: delay * (0.5 to 1.5)
                        delay = delay * (0.5 + random.random())

                    logging.info(
                        f"Attempt {attempt + 1} of {max_retries + 1} failed for {func.__name__}. "
                        f"Retrying in {delay:.2f}s. Error: {type(e).__name__}: {str(e)}"
                    )

                    time.sleep(delay)

            # This line should never be reached, but included for type checking
            raise last_exception

        return wrapper
    return decorator


def retry_operation(
    operation: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    allowed_exceptions: Optional[tuple] = None
) -> Any:
    """
    Execute an operation with retry logic.

    Args:
        operation: The operation function to execute
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which delay increases after each retry
        jitter: Whether to add random jitter to delay times
        allowed_exceptions: Tuple of exceptions that trigger a retry

    Returns:
        The result of the operation if successful

    Raises:
        The last exception if all retries fail
    """
    if allowed_exceptions is None:
        allowed_exceptions = (Exception,)

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return operation()
        except allowed_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                # Final attempt - raise the exception
                logging.warning(
                    f"Operation failed after {max_retries} retries. "
                    f"Last error: {type(e).__name__}: {str(e)}"
                )
                raise e

            # Calculate delay with exponential backoff
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)

            if jitter:
                # Add jitter: delay * (0.5 to 1.5)
                delay = delay * (0.5 + random.random())

            logging.info(
                f"Attempt {attempt + 1} of {max_retries + 1} failed. "
                f"Retrying in {delay:.2f}s. Error: {type(e).__name__}: {str(e)}"
            )

            time.sleep(delay)

    # This line should never be reached, but included for type checking
    raise last_exception


class RateLimiter:
    """
    Simple rate limiter to control the rate of API calls.
    """

    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize the rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def acquire(self):
        """
        Acquire a permit to make a call. If the rate limit is exceeded,
        sleep until a permit is available.
        """
        import time
        current_time = time.time()

        # Remove calls that are outside the time window
        self.calls = [call_time for call_time in self.calls if current_time - call_time <= self.time_window]

        if len(self.calls) >= self.max_calls:
            # Rate limit exceeded, calculate sleep time
            sleep_time = self.time_window - (current_time - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.calls.append(current_time)

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator version of rate limiter.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)
        return wrapper