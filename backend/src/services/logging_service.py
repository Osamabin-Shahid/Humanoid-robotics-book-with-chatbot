"""
Logging Service

This module provides logging infrastructure for the RAG retrieval and validation system.
It handles logging of retrieval results, errors, and other operations for reproducibility.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.models.log_entry_model import LogEntry
from src.config.settings import Settings


class LoggingService:
    """
    Service for handling logging of operations in the RAG retrieval and validation system.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the logging service with settings.
        """
        self.settings = settings
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up the logger with appropriate configuration.
        """
        logger = logging.getLogger("rag_retrieval")
        logger.setLevel(logging.INFO)

        # Create console handler if it doesn't exist
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def log_operation(self, operation_type: str, status: str, details: Optional[Dict[str, Any]] = None,
                     query_id: Optional[str] = None, result_ids: Optional[list] = None,
                     parameters: Optional[Dict[str, Any]] = None) -> LogEntry:
        """
        Log an operation with the specified parameters.

        Args:
            operation_type: Type of operation (query, validation, retrieval, error)
            status: Operation status (success, error, partial, timeout)
            details: Additional operation details
            query_id: ID of associated query
            result_ids: IDs of associated results
            parameters: Operation parameters

        Returns:
            LogEntry: The created log entry
        """
        log_id = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{operation_type}"
        timestamp = datetime.now().isoformat()

        log_entry = LogEntry(
            log_id=log_id,
            operation_type=operation_type,
            timestamp=timestamp,
            status=status,
            query_id=query_id,
            result_ids=result_ids,
            parameters=parameters,
            details=details
        )

        # Validate the log entry
        log_entry.validate()

        # Log to the configured logger
        message = f"{operation_type} operation - Status: {status}"
        if details:
            message += f" - Details: {json.dumps(details, default=str)[:200]}..."  # Truncate long details

        if status.lower() in ['error', 'timeout']:
            self.logger.error(message)
        elif status.lower() in ['partial']:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return log_entry

    def log_retrieval(self, query_id: str, result_count: int, query_text: str,
                      execution_time: Optional[float] = None) -> LogEntry:
        """
        Log a retrieval operation.

        Args:
            query_id: ID of the query
            result_count: Number of results retrieved
            query_text: The original query text (truncated for logging)
            execution_time: Time taken for the operation in seconds

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'result_count': result_count,
            'query_text_truncated': query_text[:100] + "..." if len(query_text) > 100 else query_text
        }

        if execution_time is not None:
            details['execution_time_seconds'] = execution_time

        return self.log_operation(
            operation_type="retrieval",
            status="success",
            details=details,
            query_id=query_id
        )

    def log_retrieval_error(self, query_id: str, error_message: str,
                            query_text: Optional[str] = None) -> LogEntry:
        """
        Log a retrieval error.

        Args:
            query_id: ID of the query that failed
            error_message: Error message
            query_text: The original query text (optional)

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'error_message': error_message
        }

        if query_text:
            details['query_text_truncated'] = query_text[:100] + "..." if len(query_text) > 100 else query_text

        return self.log_operation(
            operation_type="retrieval",
            status="error",
            details=details,
            query_id=query_id
        )

    def log_validation(self, result_id: str, validation_score: float,
                      issues_found: Optional[list] = None,
                      validation_type: Optional[str] = None) -> LogEntry:
        """
        Log a validation operation.

        Args:
            result_id: ID of the result being validated
            validation_score: Score from the validation
            issues_found: List of issues found during validation
            validation_type: Type of validation (metadata, content, coherence, etc.)

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'result_id': result_id,
            'validation_score': validation_score
        }

        if validation_type:
            details['validation_type'] = validation_type

        if issues_found:
            details['issues_found_count'] = len(issues_found)
            details['issues_found_sample'] = issues_found[:3]  # Show first 3 issues

        return self.log_operation(
            operation_type="validation",
            status="success",
            details=details
        )

    def log_chunk_effectiveness(self, result_id: str, chunk_metrics: Dict[str, Any]) -> LogEntry:
        """
        Log chunk effectiveness metrics.

        Args:
            result_id: ID of the result being evaluated
            chunk_metrics: Dictionary containing chunk effectiveness metrics

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'result_id': result_id,
            'chunk_metrics': chunk_metrics
        }

        return self.log_operation(
            operation_type="chunk_effectiveness",
            status="success",
            details=details
        )

    def log_pipeline_validation(self, validation_type: str, metrics: Dict[str, Any],
                              issues: Optional[List[str]] = None) -> LogEntry:
        """
        Log pipeline validation results.

        Args:
            validation_type: Type of pipeline validation (integrity, reproducibility, etc.)
            metrics: Dictionary containing validation metrics
            issues: List of issues found during validation

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'validation_type': validation_type,
            'metrics': metrics
        }

        if issues:
            details['issues_count'] = len(issues)
            details['issues_sample'] = issues[:5]  # Show first 5 issues

        return self.log_operation(
            operation_type="pipeline_validation",
            status="completed",
            details=details
        )

    def log_retrieval_with_effectiveness(self, query_id: str, result_count: int, query_text: str,
                                       effectiveness_metrics: Optional[Dict[str, Any]] = None,
                                       execution_time: Optional[float] = None) -> LogEntry:
        """
        Log a retrieval operation with effectiveness metrics.

        Args:
            query_id: ID of the query
            result_count: Number of results retrieved
            query_text: The original query text (truncated for logging)
            effectiveness_metrics: Dictionary containing effectiveness metrics
            execution_time: Time taken for the operation in seconds

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'result_count': result_count,
            'query_text_truncated': query_text[:100] + "..." if len(query_text) > 100 else query_text
        }

        if execution_time is not None:
            details['execution_time_seconds'] = execution_time

        if effectiveness_metrics:
            details['effectiveness_metrics'] = effectiveness_metrics

        return self.log_operation(
            operation_type="retrieval_with_effectiveness",
            status="success",
            details=details,
            query_id=query_id
        )

    def log_validation_error(self, result_id: str, error_message: str) -> LogEntry:
        """
        Log a validation error.

        Args:
            result_id: ID of the result that failed validation
            error_message: Error message

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'result_id': result_id,
            'error_message': error_message
        }

        return self.log_operation(
            operation_type="validation",
            status="error",
            details=details
        )

    def log_query(self, query_id: str, query_text: str, limit: int,
                  execution_time: Optional[float] = None) -> LogEntry:
        """
        Log a query operation.

        Args:
            query_id: ID of the query
            query_text: The query text
            limit: Result limit specified
            execution_time: Time taken for the operation in seconds

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'query_text_truncated': query_text[:100] + "..." if len(query_text) > 100 else query_text,
            'limit': limit
        }

        if execution_time is not None:
            details['execution_time_seconds'] = execution_time

        return self.log_operation(
            operation_type="query",
            status="success",
            details=details,
            query_id=query_id
        )

    def log_general_error(self, operation_type: str, error_message: str,
                          context: Optional[Dict[str, Any]] = None) -> LogEntry:
        """
        Log a general error.

        Args:
            operation_type: Type of operation where error occurred
            error_message: Error message
            context: Additional context information

        Returns:
            LogEntry: The created log entry
        """
        details = {
            'error_message': error_message
        }

        if context:
            details['context'] = context

        return self.log_operation(
            operation_type=operation_type,
            status="error",
            details=details
        )

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.

        Returns:
            logging.Logger: The logger instance
        """
        return self.logger