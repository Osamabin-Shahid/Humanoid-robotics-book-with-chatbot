"""
Helpers Module

This module provides general helper functions for the RAG URL ingestion pipeline.
"""

import hashlib
import time
from typing import Any, Dict, List
from datetime import datetime


class Helpers:
    """Utility class for helper functions."""

    @staticmethod
    def generate_id(prefix: str = "id") -> str:
        """Generate a unique ID with an optional prefix."""
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """Generate a hash for content change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
        """Execute a function with retry and exponential backoff."""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e

                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)

        return None

    @staticmethod
    def format_timestamp(dt: datetime) -> str:
        """Format a datetime object as an ISO string."""
        return dt.isoformat()

    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split a list into chunks of specified size."""
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")

        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @staticmethod
    def calculate_token_count(text: str) -> int:
        """Calculate approximate token count by splitting on whitespace."""
        return len(text.split()) if text else 0