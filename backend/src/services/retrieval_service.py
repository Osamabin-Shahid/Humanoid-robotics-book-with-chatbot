"""
Retrieval Service

This module provides the main retrieval service for the RAG retrieval and validation system.
It orchestrates query processing, semantic search, and result validation.
"""
from typing import List, Optional, Dict, Any
from src.config.settings import Settings
from src.services.search_service import SemanticSearchService
from src.models.retrieval_result_model import RetrievalResult
from src.models.query_model import Query
from src.services.logging_service import LoggingService
from src.services.validation_service import ValidationService
from datetime import datetime
import uuid
import time


class RetrievalService:
    """
    Main service for retrieving relevant content from the Qdrant vector database.
    Orchestrates query processing, semantic search, and result validation.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the retrieval service with settings.
        """
        self.settings = settings
        self.search_service = SemanticSearchService(settings)
        self.validation_service = ValidationService(settings)
        self.logger = LoggingService(settings)

    def retrieve(self, query_text: str, limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Retrieve relevant content based on the query text.

        Args:
            query_text: The natural language query text
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of retrieval results

        Raises:
            ValueError: If query_text is invalid
            Exception: If retrieval fails
        """
        query_id = f"retrieval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # Validate inputs
            if not query_text or not query_text.strip():
                raise ValueError("Query text cannot be empty or just whitespace")

            if limit <= 0:
                raise ValueError(f"Limit must be positive, got {limit}")

            if not (0 <= min_score <= 1):
                raise ValueError(f"Min score must be between 0 and 1, got {min_score}")

            start_time = time.time()

            # Log the query
            self.logger.log_query(
                query_id=query_id,
                query_text=query_text,
                limit=limit,
                execution_time=None  # Will be added after execution
            )

            # Perform semantic search with error handling
            try:
                results = self.search_service.search(query_text, limit, min_score)
            except Exception as e:
                error_msg = f"Search service failed: {str(e)}"
                self.logger.log_general_error(
                    operation_type="semantic_search",
                    error_message=error_msg,
                    context={
                        "query_id": query_id,
                        "query_text": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                        "limit": limit,
                        "min_score": min_score,
                        "error_type": type(e).__name__
                    }
                )
                raise Exception(f"Search failed: {str(e)}")

            execution_time = time.time() - start_time

            # Log the retrieval with comprehensive effectiveness metrics
            try:
                effectiveness_metrics = {
                    "avg_similarity_score": sum(r.similarity_score for r in results) / len(results) if results else 0,
                    "min_similarity_score": min((r.similarity_score for r in results), default=0) if results else 0,
                    "max_similarity_score": max((r.similarity_score for r in results), default=0) if results else 0,
                    "execution_time_seconds": execution_time,
                    "result_count": len(results),
                    "query_length": len(query_text),
                    "results_with_high_score": len([r for r in results if r.similarity_score > 0.7]),
                    "results_with_medium_score": len([r for r in results if 0.3 <= r.similarity_score <= 0.7]),
                    "results_with_low_score": len([r for r in results if r.similarity_score < 0.3])
                }

                self.logger.log_retrieval_with_effectiveness(
                    query_id=query_id,
                    result_count=len(results),
                    query_text=query_text,
                    effectiveness_metrics=effectiveness_metrics,
                    execution_time=execution_time
                )

                # Log individual results for debugging (only first few to avoid log spam)
                for i, result in enumerate(results[:3]):  # Log first 3 results
                    self.logger.log_operation(
                        operation_type="retrieval",  # Changed to valid operation type
                        status="success",
                        details={
                            "query_id": query_id,
                            "result_index": i,
                            "result_id": result.result_id,
                            "similarity_score": result.similarity_score,
                            "content_length": len(result.content_text),
                            "source_url": result.source_url
                        }
                    )
            except Exception as e:
                # Even if detailed logging fails, we should still return the results
                self.logger.log_general_error(
                    operation_type="retrieval",  # Changed to valid operation type
                    error_message=f"Failed to log detailed retrieval metrics: {str(e)}",
                    context={
                        "query_id": query_id,
                        "result_count": len(results),
                        "execution_time": execution_time
                    }
                )

            return results

        except ValueError as ve:
            # Log validation errors specifically
            self.logger.log_general_error(
                operation_type="retrieval_validation",
                error_message=f"Validation error: {str(ve)}",
                context={
                    "query_id": query_id,
                    "query_text": query_text,
                    "limit": limit,
                    "min_score": min_score
                }
            )
            raise ve
        except Exception as e:
            # Log the error with more context
            self.logger.log_general_error(
                operation_type="retrieval",
                error_message=str(e),
                context={
                    "query_id": query_id,
                    "query_text": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                    "limit": limit,
                    "min_score": min_score,
                    "error_type": type(e).__name__,
                    "execution_time": time.time() if 'start_time' in locals() else None
                }
            )
            raise e

    def retrieve_and_validate(self, query_text: str, limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Retrieve relevant content and perform validation on the results.

        Args:
            query_text: The natural language query text
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of validated retrieval results
        """
        results = self.retrieve(query_text, limit, min_score)

        # Validate each result using the validation service
        validated_results = []
        for result in results:
            # Perform comprehensive validation
            validation_report = self.validation_service.validate_result_completely(result, query_text)
            if validation_report.is_valid:
                validated_results.append(result)

        return validated_results

    def retrieve_with_validation_reports(self, query_text: str, limit: int = 10, min_score: float = 0.0) -> Dict[str, Any]:
        """
        Retrieve relevant content and return both results and validation reports.

        Args:
            query_text: The natural language query text
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            Dict[str, Any]: Dictionary containing results and validation reports
        """
        results = self.retrieve(query_text, limit, min_score)

        # Generate validation reports for all results
        validation_results = self.validation_service.validate_multiple_results(results, query_text)

        return {
            "results": results,
            "validation_reports": validation_results,
            "summary": self.validation_service.get_validation_summary(results, query_text)
        }

    def validate_retrieval_quality(self, query_text: str, expected_content_keywords: List[str],
                                  limit: int = 10) -> Dict[str, Any]:
        """
        Validate the quality of retrieval results against expected content.

        Args:
            query_text: The query text
            expected_content_keywords: List of keywords expected in relevant results
            limit: Number of results to check

        Returns:
            Dict[str, Any]: Validation results including quality metrics
        """
        results = self.retrieve(query_text, limit=limit)

        # Perform comprehensive validation on results
        validation_summary = self.validation_service.get_validation_summary(results, query_text)

        # Calculate keyword relevance
        total_results = len(results)
        relevant_results = 0

        for result in results:
            content_lower = result.content_text.lower()
            # Count how many expected keywords appear in the result
            keyword_matches = sum(1 for keyword in expected_content_keywords if keyword.lower() in content_lower)
            if keyword_matches > 0:
                relevant_results += 1

        keyword_relevance_score = relevant_results / total_results if total_results > 0 else 0

        # Combine with validation metrics
        quality_score = (validation_summary["validity_percentage"] / 100 + keyword_relevance_score) / 2

        validation_report = {
            "query_text": query_text,
            "total_results": total_results,
            "relevant_results": relevant_results,
            "keyword_relevance_score": keyword_relevance_score,
            "validation_validity_percentage": validation_summary["validity_percentage"],
            "combined_quality_score": quality_score,
            "expected_keywords": expected_content_keywords,
            "relevance_percentage": (relevant_results / total_results * 100) if total_results > 0 else 0,
            "validation_summary": validation_summary
        }

        return validation_report

    def create_query_object(self, query_text: str, limit: int = 10, min_score: float = 0.0,
                           parameters: Optional[Dict[str, Any]] = None) -> Query:
        """
        Create a Query object from the query parameters.

        Args:
            query_text: The natural language query text
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold
            parameters: Additional query parameters

        Returns:
            Query: The created Query object
        """
        query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        query = Query(
            query_id=query_id,
            text=query_text,
            timestamp=timestamp,
            limit=limit,
            min_score=min_score,
            parameters=parameters
        )

        query.validate()
        return query

    def retrieve_with_query_object(self, query: Query) -> List[RetrievalResult]:
        """
        Retrieve content using a Query object.

        Args:
            query: The Query object containing query parameters

        Returns:
            List[RetrievalResult]: List of retrieval results
        """
        return self.retrieve(
            query_text=query.text,
            limit=query.limit,
            min_score=query.min_score
        )

    def validate_retrieval_quality(self, query_text: str, expected_content_keywords: List[str],
                                  limit: int = 10) -> Dict[str, Any]:
        """
        Validate the quality of retrieval results against expected content.

        Args:
            query_text: The query text
            expected_content_keywords: List of keywords expected in relevant results
            limit: Number of results to check

        Returns:
            Dict[str, Any]: Validation results including quality metrics
        """
        results = self.retrieve(query_text, limit=limit)

        total_results = len(results)
        relevant_results = 0

        for result in results:
            content_lower = result.content_text.lower()
            # Count how many expected keywords appear in the result
            keyword_matches = sum(1 for keyword in expected_content_keywords if keyword.lower() in content_lower)
            if keyword_matches > 0:
                relevant_results += 1

        quality_score = relevant_results / total_results if total_results > 0 else 0

        validation_report = {
            "query_text": query_text,
            "total_results": total_results,
            "relevant_results": relevant_results,
            "quality_score": quality_score,
            "expected_keywords": expected_content_keywords,
            "relevance_percentage": (relevant_results / total_results * 100) if total_results > 0 else 0
        }

        return validation_report

    def get_relevant_chunks_by_source(self, query_text: str, source_url: str,
                                      limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks specifically from a given source URL.

        Args:
            query_text: The query text
            source_url: The source URL to filter results from
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of retrieval results from the specified source
        """
        # First, get all results
        all_results = self.retrieve(query_text, limit * 2, min_score)  # Get more to account for filtering

        # Filter by source URL
        filtered_results = [result for result in all_results if result.source_url == source_url]

        return filtered_results[:limit]

    def search_by_topic(self, topic: str, limit: int = 10, min_score: float = 0.3) -> List[RetrievalResult]:
        """
        Search for content related to a specific topic.

        Args:
            topic: The topic to search for
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of retrieval results related to the topic
        """
        query_text = f"Information about {topic}"
        return self.retrieve(query_text, limit, min_score)

    def get_content_by_section(self, query_text: str, section_title: str,
                              limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Retrieve content from a specific section of the documentation.

        Args:
            query_text: The query text
            section_title: The section title to search within
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of retrieval results from the specified section
        """
        # This would use metadata filtering if implemented in search_service
        # For now, we'll just do a regular search and let the caller filter
        results = self.retrieve(query_text, limit, min_score)
        section_results = [result for result in results if section_title.lower() in result.metadata.get('section', '').lower()]
        return section_results