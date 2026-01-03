"""
Embedding Models

This module defines data models for embedding vectors
for the RAG URL ingestion pipeline.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmbeddingVector:
    """Data model for an embedding vector."""

    vector_id: str
    vector_data: List[float]
    model_name: str
    model_version: str
    dimension: int
    source_chunk_id: Optional[str] = None

    def validate(self) -> bool:
        """Validate the embedding vector."""
        if not self.vector_id:
            raise ValueError("vector_id is required")

        if not self.vector_data:
            raise ValueError("vector_data is required")

        if len(self.vector_data) != self.dimension:
            raise ValueError(f"vector_data length ({len(self.vector_data)}) does not match dimension ({self.dimension})")

        if not self.model_name:
            raise ValueError("model_name is required")

        if self.dimension <= 0:
            raise ValueError("dimension must be positive")

        return True

    def to_dict(self) -> dict:
        """Convert the embedding vector to a dictionary."""
        return {
            'vector_id': self.vector_id,
            'vector_data': self.vector_data,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'dimension': self.dimension,
            'source_chunk_id': self.source_chunk_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EmbeddingVector':
        """Create an EmbeddingVector from a dictionary."""
        return cls(
            vector_id=data.get('vector_id', ''),
            vector_data=data.get('vector_data', []),
            model_name=data.get('model_name', ''),
            model_version=data.get('model_version', ''),
            dimension=data.get('dimension', 0),
            source_chunk_id=data.get('source_chunk_id')
        )