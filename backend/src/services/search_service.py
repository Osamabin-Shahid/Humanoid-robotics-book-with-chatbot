"""
Search Service

This module provides semantic search functionality for the RAG retrieval and validation system.
It uses Qdrant to find semantically similar chunks based on query embeddings.
"""
from typing import List, Dict, Any
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient
from src.embedding.query_generator import QueryEmbeddingGenerator
from src.models.retrieval_result_model import RetrievalResult
from src.models.metadata_model import Metadata
from src.services.logging_service import LoggingService
from datetime import datetime
import uuid
import time


class SemanticSearchService:
    """
    Service for performing semantic search in the Qdrant vector database.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the semantic search service with settings.
        """
        self.settings = settings
        self.qdrant_client = QdrantCloudClient(settings)
        self.query_generator = QueryEmbeddingGenerator(settings)
        self.logger = LoggingService(settings)

    def search(self, query_text: str, limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Perform semantic search for the given query text.

        Args:
            query_text: The natural language query text
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of retrieval results
        """
        query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # Validate query text
            self.query_generator.validate_query_text(query_text)

            # Generate embedding for the query with error handling
            try:
                query_embedding = self.query_generator.get_query_embedding(query_text)
            except Exception as e:
                error_msg = f"Failed to generate query embedding: {str(e)}"
                self.logger.log_general_error(
                    operation_type="embedding_generation",
                    error_message=error_msg,
                    context={
                        "query_id": query_id,
                        "query_text": query_text[:100] + "..." if len(query_text) > 100 else query_text
                    }
                )
                raise Exception(f"Embedding generation failed: {str(e)}")

            # Perform semantic search in Qdrant with error handling
            try:
                search_results = self.qdrant_client.search_similar(
                    query_vector=query_embedding,
                    limit=limit
                )
            except Exception as e:
                error_msg = f"Qdrant search failed: {str(e)}"
                self.logger.log_general_error(
                    operation_type="qdrant_search",
                    error_message=error_msg,
                    context={
                        "query_id": query_id,
                        "query_text": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                        "limit": limit,
                        "embedding_dimension": len(query_embedding) if query_embedding else 0
                    }
                )
                raise Exception(f"Qdrant search failed: {str(e)}")

            # Filter results based on minimum score
            filtered_results = [result for result in search_results if result['score'] >= min_score]

            # Convert search results to RetrievalResult objects
            retrieval_results = []
            for result in filtered_results:
                try:
                    payload = result.get('payload', {})

                    # Create RetrievalResult from search result
                    retrieval_result = RetrievalResult(
                        result_id=result.get('id', ''),
                        query_text=query_text,
                        content_text=payload.get('content', payload.get('source_url', '')),
                        source_url=payload.get('source_url', ''),
                        similarity_score=result.get('score', 0.0),
                        chunk_id=payload.get('chunk_id', ''),
                        created_at=datetime.now().isoformat(),
                        metadata=payload
                    )

                    # Validate the retrieval result
                    retrieval_result.validate()
                    retrieval_results.append(retrieval_result)
                except Exception as e:
                    error_msg = f"Failed to create retrieval result from Qdrant result: {str(e)}"
                    self.logger.log_general_error(
                        operation_type="result_creation",
                        error_message=error_msg,
                        context={
                            "query_id": query_id,
                            "result_id": result.get('id', 'unknown'),
                            "payload_keys": list(result.get('payload', {}).keys()) if result.get('payload') else []
                        }
                    )
                    # Continue processing other results instead of failing the entire operation
                    continue

            # Log the successful retrieval
            self.logger.log_retrieval(
                query_id=query_id,
                result_count=len(retrieval_results),
                query_text=query_text,
            )

            return retrieval_results

        except Exception as e:
            # Log the error
            self.logger.log_retrieval_error(
                query_id=query_id,
                error_message=str(e),
                query_text=query_text
            )
            raise e

    def search_with_validation(self, query_text: str, limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Perform semantic search and validate the results.

        Args:
            query_text: The natural language query text
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of validated retrieval results
        """
        results = self.search(query_text, limit, min_score)

        # Additional validation can be added here if needed
        # For now, we return the same results with potential validation scoring
        for result in results:
            # In the future, we might add validation scores here
            pass

        return results

    def get_top_k_chunks(self, query_text: str, k: int = 5, min_score: float = 0.3) -> List[RetrievalResult]:
        """
        Get the top-k most relevant chunks for a query.

        Args:
            query_text: The natural language query text
            k: Number of top results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: Top-k retrieval results
        """
        return self.search(query_text, limit=k, min_score=min_score)

    def validate_search_result(self, result: RetrievalResult) -> bool:
        """
        Validate a single search result for quality.

        Args:
            result: The retrieval result to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            result.validate()
            return True
        except ValueError as e:
            self.logger.log_general_error(
                operation_type="validation",
                error_message=f"Invalid retrieval result: {str(e)}",
                context={
                    "result_id": result.result_id,
                    "source_url": result.source_url
                }
            )
            return False

    def search_by_metadata_filter(self, query_text: str, metadata_filters: Dict[str, Any],
                                  limit: int = 10, min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Perform semantic search with metadata filters.

        Args:
            query_text: The natural language query text
            metadata_filters: Dictionary of metadata filters to apply
            limit: Maximum number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List[RetrievalResult]: List of filtered retrieval results
        """
        # Note: This is a simplified version - actual implementation would depend on
        # Qdrant's filtering capabilities. For now, we search and then filter results.
        all_results = self.search(query_text, limit * 2, min_score)  # Get more results to account for filtering

        filtered_results = []
        for result in all_results:
            match = True
            for key, value in metadata_filters.items():
                if result.metadata and result.metadata.get(key) != value:
                    match = False
                    break

            if match:
                filtered_results.append(result)

        return filtered_results[:limit]