"""
Pipeline Configuration Model

This module defines the data model for pipeline configuration
for the RAG URL ingestion pipeline.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineConfig:
    """Data model for pipeline configuration."""

    chunk_size: int
    overlap_percentage: float
    rate_limit_requests: int
    rate_limit_period: int
    cohere_model: str = "embed-multilingual-v2.0"
    qdrant_collection: str = "book_embeddings"
    timeout_seconds: int = 30
    max_retries: int = 3

    def validate(self) -> bool:
        """Validate the pipeline configuration."""
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if not 0 <= self.overlap_percentage <= 1:
            raise ValueError("overlap_percentage must be between 0 and 1")

        if self.rate_limit_requests <= 0:
            raise ValueError("rate_limit_requests must be positive")

        if self.rate_limit_period <= 0:
            raise ValueError("rate_limit_period must be positive")

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        if self.max_retries <= 0:
            raise ValueError("max_retries must be positive")

        return True

    def to_dict(self) -> dict:
        """Convert the configuration to a dictionary."""
        return {
            'chunk_size': self.chunk_size,
            'overlap_percentage': self.overlap_percentage,
            'rate_limit_requests': self.rate_limit_requests,
            'rate_limit_period': self.rate_limit_period,
            'cohere_model': self.cohere_model,
            'qdrant_collection': self.qdrant_collection,
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PipelineConfig':
        """Create a PipelineConfig from a dictionary."""
        return cls(
            chunk_size=data.get('chunk_size', 512),
            overlap_percentage=data.get('overlap_percentage', 0.2),
            rate_limit_requests=data.get('rate_limit_requests', 10),
            rate_limit_period=data.get('rate_limit_period', 60),
            cohere_model=data.get('cohere_model', "embed-multilingual-v2.0"),
            qdrant_collection=data.get('qdrant_collection', "book_embeddings"),
            timeout_seconds=data.get('timeout_seconds', 30),
            max_retries=data.get('max_retries', 3)
        )

    @classmethod
    def from_settings(cls, settings) -> 'PipelineConfig':
        """Create a PipelineConfig from application settings."""
        return cls(
            chunk_size=settings.chunk_size,
            overlap_percentage=settings.overlap_percentage,
            rate_limit_requests=settings.rate_limit_requests,
            rate_limit_period=settings.rate_limit_period,
            timeout_seconds=settings.timeout_seconds,
            max_retries=settings.max_retries
        )