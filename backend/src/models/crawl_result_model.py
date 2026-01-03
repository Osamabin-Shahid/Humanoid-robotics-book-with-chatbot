"""
Crawl Result Model

This module defines the data model for crawl results
for the RAG URL ingestion pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class CrawlResult:
    """Data model for a crawl operation result."""

    crawl_id: str
    source_url: str
    status: str  # 'success', 'partial', 'failed'
    start_time: datetime
    end_time: datetime
    pages_processed: int = 0
    total_chunks: int = 0
    error_count: int = 0
    processed_urls: List[str] = field(default_factory=list)
    error_details: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    incremental: bool = False  # Flag for incremental updates
    updated_chunks: int = 0  # Number of chunks that were updated
    unchanged_chunks: int = 0  # Number of chunks that were unchanged

    def validate(self) -> bool:
        """Validate the crawl result."""
        if not self.crawl_id:
            raise ValueError("crawl_id is required")

        if not self.source_url:
            raise ValueError("source_url is required")

        if self.status not in ['success', 'partial', 'failed']:
            raise ValueError("status must be 'success', 'partial', or 'failed'")

        if self.end_time < self.start_time:
            raise ValueError("end_time must be after start_time")

        if self.pages_processed < 0:
            raise ValueError("pages_processed must be non-negative")

        if self.total_chunks < 0:
            raise ValueError("total_chunks must be non-negative")

        if self.error_count < 0:
            raise ValueError("error_count must be non-negative")

        return True

    def to_dict(self) -> dict:
        """Convert the crawl result to a dictionary."""
        return {
            'crawl_id': self.crawl_id,
            'source_url': self.source_url,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'pages_processed': self.pages_processed,
            'total_chunks': self.total_chunks,
            'error_count': self.error_count,
            'processed_urls': self.processed_urls,
            'error_details': self.error_details,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CrawlResult':
        """Create a CrawlResult from a dictionary."""
        from datetime import datetime
        return cls(
            crawl_id=data.get('crawl_id', ''),
            source_url=data.get('source_url', ''),
            status=data.get('status', 'failed'),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else datetime.now(),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else datetime.now(),
            pages_processed=data.get('pages_processed', 0),
            total_chunks=data.get('total_chunks', 0),
            error_count=data.get('error_count', 0),
            processed_urls=data.get('processed_urls', []),
            error_details=data.get('error_details', []),
            metadata=data.get('metadata', {})
        )