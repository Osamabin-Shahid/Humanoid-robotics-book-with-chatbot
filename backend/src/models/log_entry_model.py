"""
Log Entry Model

This module defines the data model for log entries
for the RAG retrieval and validation system.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class LogEntry:
    """
    Represents a logged operation for reproducibility.

    Fields:
    - log_id: Unique identifier for the log entry
    - operation_type: Type of operation (query, validation, retrieval, error)
    - timestamp: When the operation occurred
    - query_id: ID of associated query (optional)
    - result_ids: IDs of associated results (optional)
    - parameters: Operation parameters (optional)
    - status: Operation status (success, error, partial, timeout)
    - details: Additional operation details (optional)
    """

    log_id: str
    operation_type: str  # Must be one of: "query", "validation", "retrieval", "error"
    timestamp: str  # ISO format datetime string
    status: str  # Must be one of: "success", "error", "partial", "timeout"
    query_id: Optional[str] = None
    result_ids: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None

    def validate(self) -> bool:
        """Validate the log entry."""
        if not self.log_id:
            raise ValueError("log_id is required")

        if not self.operation_type:
            raise ValueError("operation_type is required")

        if self.operation_type not in ["query", "validation", "retrieval", "error"]:
            raise ValueError("operation_type must be one of: 'query', 'validation', 'retrieval', 'error'")

        if not self.timestamp:
            raise ValueError("timestamp is required")

        if not self.status:
            raise ValueError("status is required")

        if self.status not in ["success", "error", "partial", "timeout"]:
            raise ValueError("status must be one of: 'success', 'error', 'partial', 'timeout'")

        return True

    def to_dict(self) -> dict:
        """Convert the log entry to a dictionary."""
        result = {
            'log_id': self.log_id,
            'operation_type': self.operation_type,
            'timestamp': self.timestamp,
            'status': self.status
        }

        if self.query_id:
            result['query_id'] = self.query_id

        if self.result_ids:
            result['result_ids'] = self.result_ids

        if self.parameters:
            result['parameters'] = self.parameters

        if self.details:
            result['details'] = self.details

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'LogEntry':
        """Create a LogEntry object from a dictionary."""
        return cls(
            log_id=data.get('log_id', ''),
            operation_type=data.get('operation_type', ''),
            timestamp=data.get('timestamp', ''),
            status=data.get('status', ''),
            query_id=data.get('query_id'),
            result_ids=data.get('result_ids'),
            parameters=data.get('parameters'),
            details=data.get('details')
        )