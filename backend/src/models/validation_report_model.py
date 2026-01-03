"""
Validation Report Model

This module defines the data model for validation reports
for the RAG retrieval and validation system.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ValidationReport:
    """
    Represents the validation results for a retrieval operation.

    Fields:
    - validation_id: Unique identifier for the validation
    - result_id: ID of the result being validated
    - alignment_valid: Whether metadata aligns with content
    - metadata_correct: Whether metadata is accurate
    - content_coherent: Whether content is coherent
    - overall_score: Overall validation score (0.0-1.0)
    - validation_timestamp: When validation was performed
    - issues_found: List of validation issues (optional)
    """

    validation_id: str
    result_id: str
    alignment_valid: bool
    metadata_correct: bool
    content_coherent: bool
    overall_score: float  # Must be between 0.0 and 1.0
    validation_timestamp: str  # ISO format datetime string
    issues_found: Optional[List[str]] = None

    def validate(self) -> bool:
        """Validate the validation report."""
        if not self.validation_id:
            raise ValueError("validation_id is required")

        if not self.result_id:
            raise ValueError("result_id is required")

        if self.overall_score is None or not 0.0 <= self.overall_score <= 1.0:
            raise ValueError("overall_score must be between 0.0 and 1.0")

        if not self.validation_timestamp:
            raise ValueError("validation_timestamp is required")

        # All boolean validation fields must be present
        if self.alignment_valid is None:
            raise ValueError("alignment_valid is required")

        if self.metadata_correct is None:
            raise ValueError("metadata_correct is required")

        if self.content_coherent is None:
            raise ValueError("content_coherent is required")

        return True

    def to_dict(self) -> dict:
        """Convert the validation report to a dictionary."""
        result = {
            'validation_id': self.validation_id,
            'result_id': self.result_id,
            'alignment_valid': self.alignment_valid,
            'metadata_correct': self.metadata_correct,
            'content_coherent': self.content_coherent,
            'overall_score': self.overall_score,
            'validation_timestamp': self.validation_timestamp
        }

        if self.issues_found:
            result['issues_found'] = self.issues_found

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationReport':
        """Create a ValidationReport object from a dictionary."""
        return cls(
            validation_id=data.get('validation_id', ''),
            result_id=data.get('result_id', ''),
            alignment_valid=data.get('alignment_valid', False),
            metadata_correct=data.get('metadata_correct', False),
            content_coherent=data.get('content_coherent', False),
            overall_score=data.get('overall_score', 0.0),
            validation_timestamp=data.get('validation_timestamp', ''),
            issues_found=data.get('issues_found')
        )