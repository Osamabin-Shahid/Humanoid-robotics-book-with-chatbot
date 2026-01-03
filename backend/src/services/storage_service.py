"""
Storage Service

This module manages the vector storage process
for the RAG URL ingestion pipeline.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient
from src.embedding.models import EmbeddingVector
from src.storage.models import Metadata, StorageResult
from src.models.chunk_model import TextChunk


class StorageService:
    """Service to manage the vector storage process."""

    def __init__(self, settings: Settings):
        """Initialize the storage service with settings."""
        self.settings = settings
        self.client = QdrantCloudClient(settings)

    def initialize_storage(self, vector_size: int = 768, distance: str = "COSINE") -> bool:
        """Initialize storage by creating the collection if needed."""
        try:
            # Create collection with the specified vector size
            result = self.client.create_collection(vector_size=vector_size, distance=distance)
            return result
        except Exception as e:
            raise Exception(f"Error initializing storage: {str(e)}")

    def store_embedding_with_metadata(self, embedding: EmbeddingVector, chunk: TextChunk) -> bool:
        """Store a single embedding with its metadata."""
        try:
            # Create metadata from the text chunk
            metadata = Metadata(
                chunk_id=chunk.chunk_id,
                source_url=chunk.source_url,
                section=chunk.section,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                content_hash=chunk.hash,
                token_count=chunk.token_count
            )
            metadata.validate()

            # Store in Qdrant
            result = self.client.store_embedding(embedding, metadata)
            return result
        except Exception as e:
            raise Exception(f"Error storing embedding with metadata: {str(e)}")

    def update_embedding_with_metadata(self, embedding: EmbeddingVector, chunk: TextChunk) -> bool:
        """Update an existing embedding with new metadata."""
        try:
            # Create updated metadata from the text chunk
            metadata = Metadata(
                chunk_id=chunk.chunk_id,
                source_url=chunk.source_url,
                section=chunk.section,
                updated_at=datetime.now().isoformat(),
                content_hash=chunk.hash,
                token_count=chunk.token_count
            )
            metadata.validate()

            # Store in Qdrant (upsert operation)
            result = self.client.store_embedding(embedding, metadata)
            return result
        except Exception as e:
            raise Exception(f"Error updating embedding with metadata: {str(e)}")

    def store_embeddings_with_metadata(self, embeddings: List[EmbeddingVector], chunks: List[TextChunk]) -> StorageResult:
        """Store multiple embeddings with their metadata."""
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")

        stored_count = 0
        error_count = 0
        errors = []

        try:
            # Prepare metadata for all chunks
            metadata_list = []
            for chunk in chunks:
                metadata = Metadata(
                    chunk_id=chunk.chunk_id,
                    source_url=chunk.source_url,
                    section=chunk.section,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    content_hash=chunk.hash,
                    token_count=chunk.token_count
                )
                metadata.validate()
                metadata_list.append(metadata)

            # Store all embeddings at once
            stored_count = self.client.store_embeddings(embeddings, metadata_list)

            return StorageResult(
                success=True,
                message=f"Successfully stored {stored_count} embeddings",
                stored_count=stored_count,
                error_count=0
            )
        except Exception as e:
            error_count = len(embeddings)
            errors.append(str(e))
            return StorageResult(
                success=False,
                message=f"Error storing embeddings: {str(e)}",
                stored_count=0,
                error_count=error_count,
                errors=errors
            )

    def store_embeddings_with_retry(self, embeddings: List[EmbeddingVector], chunks: List[TextChunk]) -> StorageResult:
        """Store embeddings with retry logic for rate limits."""
        max_retries = self.settings.max_retries
        base_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                result = self.store_embeddings_with_metadata(embeddings, chunks)
                if result.success:
                    return result
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e

                # Wait before retrying
                import time
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Storage error, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)

        return StorageResult(
            success=False,
            message="Failed to store embeddings after all retry attempts",
            stored_count=0,
            error_count=len(embeddings)
        )

    def search_similar_content(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar content using the query vector."""
        try:
            results = self.client.search_similar(query_vector, limit)
            return results
        except Exception as e:
            raise Exception(f"Error searching for similar content: {str(e)}")

    def verify_storage_success(self, vector_id: str) -> bool:
        """Verify that a specific embedding was successfully stored."""
        try:
            return self.client.verify_storage(vector_id)
        except Exception as e:
            raise Exception(f"Error verifying storage: {str(e)}")

    def get_embedding_by_id(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific embedding by its ID."""
        try:
            return self.client.get_embedding(vector_id)
        except Exception as e:
            raise Exception(f"Error retrieving embedding: {str(e)}")

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about the storage."""
        try:
            count = self.client.count_vectors()
            return {
                'vector_count': count,
                'collection_name': self.settings.qdrant_collection_name,
                'status': 'healthy' if self.client.health_check() else 'unhealthy'
            }
        except Exception as e:
            raise Exception(f"Error getting storage stats: {str(e)}")

    def health_check(self) -> bool:
        """Perform a health check on the storage service."""
        return self.client.health_check()