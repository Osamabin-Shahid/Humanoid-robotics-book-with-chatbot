"""
Configuration and Settings for RAG URL Pipeline

This module handles loading and managing configuration settings
from environment variables for the RAG URL ingestion pipeline.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """Configuration settings for the RAG URL pipeline."""

    def __init__(self):
        """Initialize settings by loading environment variables."""
        # Load environment variables from .env file
        load_dotenv()

        # Cohere API settings
        self.cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        self.cohere_model: str = os.getenv("COHERE_MODEL", "embed-multilingual-v2.0")

        # Qdrant settings
        self.qdrant_url: str = os.getenv("QDRANT_URL", "")
        if not self.qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")

        self.qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
        self.qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "book_embeddings")

        # Pipeline configuration
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "512"))
        self.overlap_percentage: float = float(os.getenv("OVERLAP_PERCENTAGE", "0.2"))
        self.rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
        self.rate_limit_period: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
        self.timeout_seconds: int = int(os.getenv("TIMEOUT_SECONDS", "30"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))

    def validate(self) -> bool:
        """Validate that all required settings are present and correct."""
        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY is required")

        if not self.qdrant_url:
            raise ValueError("QDRANT_URL is required")

        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be positive")

        if not 0 <= self.overlap_percentage <= 1:
            raise ValueError("OVERLAP_PERCENTAGE must be between 0 and 1")

        if self.rate_limit_requests <= 0:
            raise ValueError("RATE_LIMIT_REQUESTS must be positive")

        if self.rate_limit_period <= 0:
            raise ValueError("RATE_LIMIT_PERIOD must be positive")

        if self.timeout_seconds <= 0:
            raise ValueError("TIMEOUT_SECONDS must be positive")

        if self.max_retries <= 0:
            raise ValueError("MAX_RETRIES must be positive")

        return True