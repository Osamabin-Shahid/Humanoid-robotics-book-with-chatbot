from typing import List
import logging
from ..models.agent_query import AgentQuery, RetrievedChunk
from ..retrieval.qdrant_client import qdrant_client
from ..config.settings import settings
from ..services.logging_service import logging_service


class SemanticRetrievalService:
    """
    Semantic retrieval service that integrates Qdrant client with query processing.
    Provides a higher-level interface for semantic search operations.
    """

    def __init__(self):
        """
        Initialize the semantic retrieval service.
        """
        self.qdrant_client = qdrant_client

    def retrieve_relevant_chunks(
        self,
        query: AgentQuery,
        limit: int = None,
        similarity_threshold: float = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve semantically relevant chunks for a given query.

        Args:
            query: The AgentQuery object containing the query text
            limit: Maximum number of chunks to retrieve (defaults to settings)
            similarity_threshold: Minimum similarity score (defaults to settings)

        Returns:
            List of RetrievedChunk objects containing relevant content
        """
        # Use defaults from settings if not provided
        if limit is None:
            limit = settings.max_chunks_to_retrieve
        if similarity_threshold is None:
            similarity_threshold = settings.similarity_threshold

        try:
            # This method would need to generate embeddings for the query
            # Since embedding generation is handled elsewhere, this service
            # would coordinate the retrieval process
            logging.info(f"Starting semantic retrieval for query: {query.text[:50]}...")

            # Note: In a complete implementation, this would:
            # 1. Generate embedding for the query text
            # 2. Call the Qdrant client to retrieve similar chunks
            # 3. Process and return the results

            # For now, we'll return an empty list as embedding generation
            # is handled in the RAG agent
            return []

        except Exception as e:
            logging.error(f"Error in semantic retrieval: {str(e)}")
            logging_service.log_error(
                error=e,
                operation_context="semantic_retrieval",
                query_id=query.query_id
            )
            return []

    def retrieve_chunks_with_embeddings(
        self,
        query_embedding: List[float],
        limit: int = None,
        similarity_threshold: float = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve chunks using a pre-generated embedding vector.

        Args:
            query_embedding: The embedding vector for the query
            limit: Maximum number of chunks to retrieve (defaults to settings)
            similarity_threshold: Minimum similarity score (defaults to settings)

        Returns:
            List of RetrievedChunk objects containing relevant content
        """
        # Use defaults from settings if not provided
        if limit is None:
            limit = settings.max_chunks_to_retrieve
        if similarity_threshold is None:
            similarity_threshold = settings.similarity_threshold

        try:
            # Call the Qdrant client to retrieve similar chunks
            retrieved_chunks = self.qdrant_client.retrieve_chunks(
                query_vector=query_embedding,
                limit=limit,
                similarity_threshold=similarity_threshold
            )

            return retrieved_chunks

        except Exception as e:
            logging.error(f"Error retrieving chunks with embeddings: {str(e)}")
            # Log the error but don't expose internal details to the caller
            return []

    def validate_retrieval_config(self) -> bool:
        """
        Validate that the retrieval service is properly configured.

        Returns:
            True if the service is properly configured, False otherwise
        """
        try:
            # Check if we can connect to Qdrant
            return self.qdrant_client.check_connection()
        except Exception:
            return False

    def get_retrieval_statistics(self) -> dict:
        """
        Get statistics about the retrieval service.

        Returns:
            Dictionary with retrieval statistics
        """
        try:
            # Get the embedding dimension from Qdrant
            embedding_dimension = self.qdrant_client.get_embedding_dimension()

            stats = {
                "qdrant_connection": self.qdrant_client.check_connection(),
                "embedding_dimension": embedding_dimension,
                "collection_name": settings.qdrant_collection_name,
                "default_limit": settings.max_chunks_to_retrieve,
                "default_similarity_threshold": settings.similarity_threshold
            }

            return stats
        except Exception as e:
            logging.error(f"Error getting retrieval statistics: {str(e)}")
            return {
                "qdrant_connection": False,
                "error": str(e)
            }


# Global semantic retrieval service instance
semantic_retrieval_service = SemanticRetrievalService()