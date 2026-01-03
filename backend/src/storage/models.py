"""
Storage Models

This module defines data models for storage operations
for the RAG URL ingestion pipeline.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Metadata:
    """Data model for metadata associated with embeddings."""

    chunk_id: str
    source_url: str
    section: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    content_hash: Optional[str] = None
    token_count: int = 0
    additional_metadata: Dict[str, Any] = None

    def validate(self) -> bool:
        """Validate the metadata."""
        if not self.chunk_id:
            raise ValueError("chunk_id is required")

        if not self.source_url:
            raise ValueError("source_url is required")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        return True

    def to_dict(self) -> dict:
        """Convert the metadata to a dictionary."""
        result = {
            'chunk_id': self.chunk_id,
            'source_url': self.source_url,
            'section': self.section,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'content_hash': self.content_hash,
            'token_count': self.token_count
        }

        if self.additional_metadata:
            result.update(self.additional_metadata)

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'Metadata':
        """Create a Metadata object from a dictionary."""
        return cls(
            chunk_id=data.get('chunk_id', ''),
            source_url=data.get('source_url', ''),
            section=data.get('section', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            content_hash=data.get('content_hash'),
            token_count=data.get('token_count', 0),
            additional_metadata={k: v for k, v in data.items()
                               if k not in ['chunk_id', 'source_url', 'section',
                                          'created_at', 'updated_at',
                                          'content_hash', 'token_count']}
        )


@dataclass
class StorageResult:
    """Data model for storage operation results."""

    success: bool
    message: str = ""
    stored_count: int = 0
    error_count: int = 0
    errors: list = None

    def validate(self) -> bool:
        """Validate the storage result."""
        if self.stored_count < 0:
            raise ValueError("stored_count must be non-negative")

        if self.error_count < 0:
            raise ValueError("error_count must be non-negative")

        return True

    def to_dict(self) -> dict:
        """Convert the storage result to a dictionary."""
        return {
            'success': self.success,
            'message': self.message,
            'stored_count': self.stored_count,
            'error_count': self.error_count,
            'errors': self.errors or []
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StorageResult':
        """Create a StorageResult from a dictionary."""
        return cls(
            success=data.get('success', False),
            message=data.get('message', ''),
            stored_count=data.get('stored_count', 0),
            error_count=data.get('error_count', 0),
            errors=data.get('errors', [])
        )