import logging
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LogOperationType(Enum):
    """Enumeration of different operation types for logging"""
    QUERY = "query"
    RETRIEVAL = "retrieval"
    RESPONSE_GENERATION = "response_generation"
    VALIDATION = "validation"
    ERROR = "error"
    HEALTH_CHECK = "health_check"


class LoggingService:
    """
    Logging infrastructure for the RAG agent system.
    Provides structured logging for query results, errors, and system operations.
    """

    def __init__(self, name: str = "RAGAgent"):
        """
        Initialize the logging service.

        Args:
            name: Name of the logger (default: "RAGAgent")
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def log_operation(
        self,
        operation_type: LogOperationType,
        message: str,
        query_id: Optional[str] = None,
        response_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an operation with structured information.

        Args:
            operation_type: Type of operation being logged
            message: Log message
            query_id: Optional query identifier
            response_id: Optional response identifier
            extra_data: Optional additional data to log
        """
        log_data = {
            "operation_type": operation_type.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        if query_id:
            log_data["query_id"] = query_id
        if response_id:
            log_data["response_id"] = response_id
        if extra_data:
            log_data.update(extra_data)

        self.logger.info(f"OPERATION: {log_data}")

    def log_query(
        self,
        query_id: str,
        query_text: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a query operation.

        Args:
            query_id: Unique identifier for the query
            query_text: The actual query text
            user_context: Optional user context information
        """
        self.log_operation(
            operation_type=LogOperationType.QUERY,
            message=f"Processing query: {query_text[:50]}...",
            query_id=query_id,
            extra_data={
                "query_length": len(query_text),
                "user_context": user_context or {}
            }
        )

    def log_retrieval(
        self,
        query_id: str,
        num_chunks_retrieved: int,
        retrieval_time_ms: float,
        similarity_threshold: float
    ) -> None:
        """
        Log a retrieval operation.

        Args:
            query_id: Query identifier associated with this retrieval
            num_chunks_retrieved: Number of chunks retrieved
            retrieval_time_ms: Time taken for retrieval in milliseconds
            similarity_threshold: Threshold used for filtering chunks
        """
        self.log_operation(
            operation_type=LogOperationType.RETRIEVAL,
            message=f"Retrieved {num_chunks_retrieved} chunks in {retrieval_time_ms:.2f}ms",
            query_id=query_id,
            extra_data={
                "num_chunks_retrieved": num_chunks_retrieved,
                "retrieval_time_ms": retrieval_time_ms,
                "similarity_threshold": similarity_threshold
            }
        )

    def log_response_generation(
        self,
        query_id: str,
        response_id: str,
        response_length: int,
        generation_time_ms: float,
        confidence_score: float
    ) -> None:
        """
        Log a response generation operation.

        Args:
            query_id: Query identifier associated with this response
            response_id: Response identifier
            response_length: Length of the generated response
            generation_time_ms: Time taken for response generation in milliseconds
            confidence_score: Confidence score of the response
        """
        self.log_operation(
            operation_type=LogOperationType.RESPONSE_GENERATION,
            message=f"Generated response of {response_length} characters in {generation_time_ms:.2f}ms",
            query_id=query_id,
            response_id=response_id,
            extra_data={
                "response_length": response_length,
                "generation_time_ms": generation_time_ms,
                "confidence_score": confidence_score
            }
        )

    def log_validation(
        self,
        query_id: str,
        response_id: str,
        is_valid: bool,
        validation_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a validation operation.

        Args:
            query_id: Query identifier
            response_id: Response identifier
            is_valid: Whether the response passed validation
            validation_details: Additional validation information
        """
        status = "PASSED" if is_valid else "FAILED"
        self.log_operation(
            operation_type=LogOperationType.VALIDATION,
            message=f"Response validation {status}",
            query_id=query_id,
            response_id=response_id,
            extra_data={
                "is_valid": is_valid,
                "validation_details": validation_details or {}
            }
        )

    def log_error(
        self,
        error: Exception,
        operation_context: str,
        query_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with detailed information.

        Args:
            error: The exception that occurred
            operation_context: Context of the operation where error occurred
            query_id: Optional query identifier
            extra_data: Optional additional data to log
        """
        self.log_operation(
            operation_type=LogOperationType.ERROR,
            message=f"Error in {operation_context}: {str(error)}",
            query_id=query_id,
            extra_data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "operation_context": operation_context,
                **(extra_data or {})
            }
        )

    def log_health_check(
        self,
        service_name: str,
        is_healthy: bool,
        response_time_ms: Optional[float] = None
    ) -> None:
        """
        Log a health check operation.

        Args:
            service_name: Name of the service being checked
            is_healthy: Whether the service is healthy
            response_time_ms: Response time if applicable
        """
        status = "HEALTHY" if is_healthy else "UNHEALTHY"
        message = f"Health check for {service_name}: {status}"
        if response_time_ms:
            message += f" (response time: {response_time_ms:.2f}ms)"

        self.log_operation(
            operation_type=LogOperationType.HEALTH_CHECK,
            message=message,
            extra_data={
                "service_name": service_name,
                "is_healthy": is_healthy,
                "response_time_ms": response_time_ms
            }
        )


# Global logging service instance
logging_service = LoggingService()