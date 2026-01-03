"""
Validators Module

This module provides validation utilities for the RAG URL ingestion pipeline.
"""

from urllib.parse import urlparse
from typing import List


class Validators:
    """Utility class for validation functions."""

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate if a string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def are_valid_urls(urls: List[str]) -> bool:
        """Validate if a list of strings are all valid URLs."""
        return all(Validators.is_valid_url(url) for url in urls)

    @staticmethod
    def is_valid_percentage(value: float) -> bool:
        """Validate if a value is a valid percentage (0-1)."""
        return 0 <= value <= 1

    @staticmethod
    def is_positive_integer(value: int) -> bool:
        """Validate if a value is a positive integer."""
        return value > 0

    @staticmethod
    def is_positive_number(value: float) -> bool:
        """Validate if a value is a positive number."""
        return value > 0