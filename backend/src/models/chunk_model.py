"""
Text Chunk Model

This module defines the data model for text chunks
for the RAG URL ingestion pipeline.
"""

import hashlib
from dataclasses import dataclass
from typing import Optional


@dataclass
class TextChunk:
    """Data model for a text chunk."""

    chunk_id: str
    content: str
    source_url: str
    section: str = ""
    sequence_number: int = 0
    token_count: int = 0
    hash: Optional[str] = None

    def __post_init__(self):
        """Calculate hash if not provided."""
        if self.hash is None and self.content:
            self.hash = self._generate_content_hash(self.content)

    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def validate(self) -> bool:
        """Validate the text chunk."""
        if not self.chunk_id:
            raise ValueError("chunk_id is required")

        if not self.content:
            raise ValueError("content is required")

        if not self.source_url:
            raise ValueError("source_url is required")

        if self.token_count < 0:
            raise ValueError("token_count must be non-negative")

        return True

    def get_content_length(self) -> int:
        """Get the length of the content."""
        return len(self.content) if self.content else 0

    def calculate_token_count(self) -> int:
        """Calculate approximate token count by splitting on whitespace."""
        return len(self.content.split()) if self.content else 0

    def to_dict(self) -> dict:
        """Convert the chunk to a dictionary."""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'source_url': self.source_url,
            'section': self.section,
            'sequence_number': self.sequence_number,
            'token_count': self.token_count,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TextChunk':
        """Create a TextChunk from a dictionary."""
        return cls(
            chunk_id=data.get('chunk_id', ''),
            content=data.get('content', ''),
            source_url=data.get('source_url', ''),
            section=data.get('section', ''),
            sequence_number=data.get('sequence_number', 0),
            token_count=data.get('token_count', 0),
            hash=data.get('hash')
        )