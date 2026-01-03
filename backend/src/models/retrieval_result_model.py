"""
Retrieval Result Model

This module defines the data model for retrieval results
for the RAG retrieval and validation system.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class RetrievalResult:
    """
    Represents a single retrieved result from the semantic search.

    Fields:
    - result_id: Unique identifier for this result
    - query_text: The original query text
    - content_text: The retrieved text chunk content
    - source_url: URL of the original document
    - similarity_score: Similarity score from semantic search (0.0-1.0)
    - chunk_id: ID of the original text chunk
    - created_at: When the result was retrieved
    - validation_score: Score from validation process (optional)
    - metadata: Additional metadata from the original chunk (optional)
    """

    result_id: str
    query_text: str
    content_text: str
    source_url: str
    similarity_score: float  # Must be between 0.0 and 1.0
    chunk_id: str
    created_at: str  # ISO format datetime string
    validation_score: Optional[float] = None  # Must be between 0.0 and 1.0 if present
    metadata: Optional[Dict[str, Any]] = None

    def validate(self) -> bool:
        """Validate the retrieval result."""
        if not self.result_id:
            raise ValueError("result_id is required")

        if not self.query_text:
            raise ValueError("query_text is required")

        if not self.content_text:
            raise ValueError("content_text is required")

        if not self.source_url:
            raise ValueError("source_url is required")

        if not 0.0 <= self.similarity_score <= 1.0:
            raise ValueError("similarity_score must be between 0.0 and 1.0")

        if not self.chunk_id:
            raise ValueError("chunk_id is required")

        if not self.created_at:
            raise ValueError("created_at is required")

        if self.validation_score is not None and not 0.0 <= self.validation_score <= 1.0:
            raise ValueError("validation_score must be between 0.0 and 1.0")

        return True

    def to_dict(self) -> dict:
        """Convert the retrieval result to a dictionary."""
        result = {
            'result_id': self.result_id,
            'query_text': self.query_text,
            'content_text': self.content_text,
            'source_url': self.source_url,
            'similarity_score': self.similarity_score,
            'chunk_id': self.chunk_id,
            'created_at': self.created_at
        }

        if self.validation_score is not None:
            result['validation_score'] = self.validation_score

        if self.metadata:
            result['metadata'] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'RetrievalResult':
        """Create a RetrievalResult object from a dictionary."""
        return cls(
            result_id=data.get('result_id', ''),
            query_text=data.get('query_text', ''),
            content_text=data.get('content_text', ''),
            source_url=data.get('source_url', ''),
            similarity_score=data.get('similarity_score', 0.0),
            chunk_id=data.get('chunk_id', ''),
            created_at=data.get('created_at', ''),
            validation_score=data.get('validation_score'),
            metadata=data.get('metadata')
        )