from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional
import logging
from ..models.agent_query import RetrievedChunk
from ..config.settings import settings
from ..services.retry_utils import retry_with_backoff


class QdrantRetrievalClient:
    """
    Qdrant client integration for retrieving semantically relevant chunks from the collection.
    """

    def __init__(self):
        """
        Initialize the Qdrant client with configuration from settings.
        """
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            # Use HTTPS for secure connection
            https=True
        )
        self.collection_name = settings.qdrant_collection_name

    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        backoff_factor=2.0,
        exceptions=(Exception,)
    )
    def retrieve_chunks(
        self,
        query_vector: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[RetrievedChunk]:
        """
        Retrieve semantically relevant chunks from the Qdrant collection.

        Args:
            query_vector: Vector representation of the query
            limit: Maximum number of chunks to retrieve
            similarity_threshold: Minimum similarity score for filtering results

        Returns:
            List of RetrievedChunk objects containing the most relevant content
        """
        try:
            # Validate inputs
            if not query_vector:
                logging.error("Query vector is empty or None")
                return []

            if limit <= 0:
                logging.error(f"Limit must be positive, got {limit}")
                return []

            if not (0.0 <= similarity_threshold <= 1.0):
                logging.error(f"Similarity threshold must be between 0 and 1, got {similarity_threshold}")
                return []

            # Perform semantic search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=similarity_threshold
            )

            # Convert search results to RetrievedChunk objects
            retrieved_chunks = []
            for result in search_results:
                if result.score >= similarity_threshold:
                    # Extract content and metadata from the search result
                    payload = result.payload
                    chunk = RetrievedChunk(
                        chunk_id=str(result.id),
                        content_text=payload.get("content", ""),
                        source_url=payload.get("source_url", ""),
                        similarity_score=result.score,
                        metadata=payload.get("metadata", {})
                    )
                    retrieved_chunks.append(chunk)

            return retrieved_chunks

        except Exception as e:
            logging.error(f"Error retrieving chunks from Qdrant: {str(e)}")
            raise

    @retry_with_backoff(
        max_retries=2,
        base_delay=0.5,
        backoff_factor=2.0,
        exceptions=(Exception,)
    )
    def check_connection(self) -> bool:
        """
        Check if the Qdrant client can connect to the collection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get collection info to verify connection
            collection_info = self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            logging.error(f"Qdrant connection check failed: {str(e)}")
            return False

    def get_embedding_dimension(self) -> Optional[int]:
        """
        Get the embedding dimension of the collection.

        Returns:
            Dimension of embeddings in the collection, or None if unable to determine
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            # Extract the vector size from the collection configuration
            if hasattr(collection_info, 'config') and collection_info.config:
                vector_params = collection_info.config.params.vectors
                if isinstance(vector_params, dict):
                    # If multiple vector configurations exist, return the first one's size
                    for vector_name, vector_config in vector_params.items():
                        if hasattr(vector_config, 'size'):
                            return vector_config.size
                elif hasattr(vector_params, 'size'):
                    # If single vector configuration
                    return vector_params.size
            return None
        except Exception as e:
            logging.error(f"Error getting embedding dimension: {str(e)}")
            return None


# Global Qdrant client instance
qdrant_client = QdrantRetrievalClient()