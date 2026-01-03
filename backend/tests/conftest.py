"""
Test Configuration for RAG URL Pipeline

This file contains shared test configuration and fixtures
for the RAG URL ingestion pipeline tests.
"""

import pytest
from src.config.settings import Settings


@pytest.fixture
def sample_settings():
    """Provide a sample settings object for testing."""
    return Settings()