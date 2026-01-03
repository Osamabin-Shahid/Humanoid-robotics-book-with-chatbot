"""
Query Model

This module defines the data model for user queries
for the RAG retrieval and validation system.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Query:
    """
    Represents a user query for content retrieval.

    Fields:
    - query_id: Unique identifier for the query
    - text: The natural language query text
    - timestamp: When the query was made
    - limit: Maximum number of results to return (optional, default: 10)
    - min_score: Minimum similarity score threshold (optional, default: 0.5)
    - parameters: Additional query parameters (optional)
    """

    query_id: str
    text: str
    timestamp: str  # ISO format datetime string
    limit: Optional[int] = 10  # Must be between 1 and 100
    min_score: Optional[float] = 0.5  # Must be between 0.0 and 1.0
    parameters: Optional[Dict[str, Any]] = None

    def validate(self) -> bool:
        """Validate the query."""
        if not self.query_id:
            raise ValueError("query_id is required")

        if not self.text:
            raise ValueError("text is required")

        if not self.timestamp:
            raise ValueError("timestamp is required")

        if self.limit is not None and (self.limit < 1 or self.limit > 100):
            raise ValueError("limit must be between 1 and 100")

        if self.min_score is not None and not 0.0 <= self.min_score <= 1.0:
            raise ValueError("min_score must be between 0.0 and 1.0")

        return True

    def to_dict(self) -> dict:
        """Convert the query to a dictionary."""
        result = {
            'query_id': self.query_id,
            'text': self.text,
            'timestamp': self.timestamp
        }

        if self.limit is not None:
            result['limit'] = self.limit

        if self.min_score is not None:
            result['min_score'] = self.min_score

        if self.parameters:
            result['parameters'] = self.parameters

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'Query':
        """Create a Query object from a dictionary."""
        return cls(
            query_id=data.get('query_id', ''),
            text=data.get('text', ''),
            timestamp=data.get('timestamp', ''),
            limit=data.get('limit', 10),
            min_score=data.get('min_score', 0.5),
            parameters=data.get('parameters')
        )