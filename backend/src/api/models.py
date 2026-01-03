"""
API Models

This module defines the data models for API request and response objects
for the RAG URL ingestion pipeline.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CrawlRequest:
    """Request model for initiating a website crawl operation."""

    urls: List[str]
    configuration: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.urls:
            raise ValueError("At least one URL must be provided")

        for url in self.urls:
            if not isinstance(url, str) or not url.strip():
                raise ValueError(f"Invalid URL: {url}")

        if self.configuration is None:
            self.configuration = {}

    def to_dict(self) -> dict:
        """Convert the request to a dictionary."""
        return {
            'urls': self.urls,
            'configuration': self.configuration
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CrawlRequest':
        """Create a CrawlRequest from a dictionary."""
        return cls(
            urls=data.get('urls', []),
            configuration=data.get('configuration', {})
        )


@dataclass
class CrawlResponse:
    """Response model for a crawl operation."""

    crawl_id: str
    status: str
    pages_processed: int
    total_chunks: int
    error_count: int
    start_time: str
    end_time: str
    processed_urls: List[str]
    error_details: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> dict:
        """Convert the response to a dictionary."""
        return {
            'crawl_id': self.crawl_id,
            'status': self.status,
            'pages_processed': self.pages_processed,
            'total_chunks': self.total_chunks,
            'error_count': self.error_count,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'processed_urls': self.processed_urls,
            'error_details': self.error_details or []
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CrawlResponse':
        """Create a CrawlResponse from a dictionary."""
        return cls(
            crawl_id=data.get('crawl_id', ''),
            status=data.get('status', ''),
            pages_processed=data.get('pages_processed', 0),
            total_chunks=data.get('total_chunks', 0),
            error_count=data.get('error_count', 0),
            start_time=data.get('start_time', ''),
            end_time=data.get('end_time', ''),
            processed_urls=data.get('processed_urls', []),
            error_details=data.get('error_details', [])
        )


@dataclass
class EmbeddingRequest:
    """Request model for generating embeddings for text chunks."""

    chunks: List[Dict[str, Any]]
    model: Optional[str] = None

    def __post_init__(self):
        """Validate the request after initialization."""
        if not self.chunks:
            raise ValueError("At least one chunk must be provided")

        for chunk in self.chunks:
            if not isinstance(chunk, dict):
                raise ValueError(f"Invalid chunk format: {chunk}")

            required_fields = ['chunk_id', 'content']
            for field in required_fields:
                if field not in chunk:
                    raise ValueError(f"Missing required field '{field}' in chunk: {chunk}")

    def to_dict(self) -> dict:
        """Convert the request to a dictionary."""
        return {
            'chunks': self.chunks,
            'model': self.model
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EmbeddingRequest':
        """Create an EmbeddingRequest from a dictionary."""
        return cls(
            chunks=data.get('chunks', []),
            model=data.get('model')
        )


@dataclass
class EmbeddingResponse:
    """Response model for embedding generation."""

    embeddings: List[Dict[str, Any]]
    model: str
    total_processed: int

    def to_dict(self) -> dict:
        """Convert the response to a dictionary."""
        return {
            'embeddings': self.embeddings,
            'model': self.model,
            'total_processed': self.total_processed
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EmbeddingResponse':
        """Create an EmbeddingResponse from a dictionary."""
        return cls(
            embeddings=data.get('embeddings', []),
            model=data.get('model', ''),
            total_processed=data.get('total_processed', 0)
        )


@dataclass
class HealthResponse:
    """Response model for health check."""

    status: str
    timestamp: str
    version: str = "1.0.0"

    def to_dict(self) -> dict:
        """Convert the response to a dictionary."""
        return {
            'status': self.status,
            'timestamp': self.timestamp,
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'HealthResponse':
        """Create a HealthResponse from a dictionary."""
        return cls(
            status=data.get('status', ''),
            timestamp=data.get('timestamp', ''),
            version=data.get('version', '1.0.0')
        )


@dataclass
class ErrorResponse:
    """Response model for errors."""

    error: Dict[str, str]

    def to_dict(self) -> dict:
        """Convert the response to a dictionary."""
        return {
            'error': self.error
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ErrorResponse':
        """Create an ErrorResponse from a dictionary."""
        return cls(
            error=data.get('error', {})
        )