"""
Qdrant Client

This module handles integration with Qdrant Cloud
for the RAG URL ingestion pipeline.
"""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from src.config.settings import Settings
from src.embedding.models import EmbeddingVector
from src.storage.models import Metadata
from src.utils.retry_utils import retry_with_exponential_backoff


class QdrantCloudClient:
    """Client for interacting with Qdrant Cloud."""

    def __init__(self, settings: Settings):
        """Initialize the Qdrant client with settings."""
        self.settings = settings
        # For Qdrant Cloud, use HTTPS with proper configuration
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            https=True,  # Force HTTPS for Qdrant Cloud
            verify=True,  # Verify SSL certificates
            timeout=30  # Set explicit timeout
        )
        self.collection_name = settings.qdrant_collection_name

    def create_collection(self, vector_size: int = 768, distance: str = "COSINE") -> bool:
        """Create a collection in Qdrant if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance[distance.upper()]
                    )
                )
                return True
            return True
        except Exception as e:
            raise Exception(f"Error creating collection: {str(e)}")

    def delete_collection(self) -> bool:
        """Delete the collection from Qdrant."""
        try:
            self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            raise Exception(f"Error deleting collection: {str(e)}")

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        allowed_exceptions=(Exception,)
    )
    def store_embedding(self, embedding: EmbeddingVector, metadata: Metadata) -> bool:
        """Store a single embedding with metadata in Qdrant."""
        try:
            # Prepare the point to be stored
            points = [
                models.PointStruct(
                    id=embedding.vector_id,
                    vector=embedding.vector_data,
                    payload={
                        "chunk_id": metadata.chunk_id,
                        "source_url": metadata.source_url,
                        "section": metadata.section,
                        "created_at": metadata.created_at,
                        "updated_at": metadata.updated_at,
                        "content_hash": metadata.content_hash,
                        "token_count": metadata.token_count,
                        **(metadata.additional_metadata or {})
                    }
                )
            ]

            # Upsert the point
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            return True
        except Exception as e:
            logging.error(f"Error storing embedding in Qdrant: {str(e)}")
            raise Exception(f"Error storing embedding: {str(e)}")

    def store_embeddings(self, embeddings: List[EmbeddingVector], metadata_list: List[Metadata]) -> int:
        """Store multiple embeddings with metadata in Qdrant."""
        if len(embeddings) != len(metadata_list):
            raise ValueError("Number of embeddings must match number of metadata entries")

        try:
            points = []
            for embedding, metadata in zip(embeddings, metadata_list):
                point = models.PointStruct(
                    id=embedding.vector_id,
                    vector=embedding.vector_data,
                    payload={
                        "chunk_id": metadata.chunk_id,
                        "source_url": metadata.source_url,
                        "section": metadata.section,
                        "created_at": metadata.created_at,
                        "updated_at": metadata.updated_at,
                        "content_hash": metadata.content_hash,
                        "token_count": metadata.token_count,
                        **(metadata.additional_metadata or {})
                    }
                )
                points.append(point)

            # Upsert all points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            return len(points)
        except Exception as e:
            raise Exception(f"Error storing embeddings: {str(e)}")

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        allowed_exceptions=(Exception,)
    )
    def search_similar(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors in Qdrant."""
        try:
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )

            results = []
            for result in search_results.points:  # query_points returns a QueryResponse object with points
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload,
                    'vector': result.vector
                })

            return results
        except Exception as e:
            logging.error(f"Error searching for similar vectors in Qdrant: {str(e)}")
            raise Exception(f"Error searching for similar vectors: {str(e)}")

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        allowed_exceptions=(Exception,)
    )
    def get_embedding(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific embedding by ID from Qdrant."""
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[vector_id]
            )

            if records:
                record = records[0]
                return {
                    'id': record.id,
                    'vector': record.vector,
                    'payload': record.payload
                }

            return None
        except Exception as e:
            logging.error(f"Error retrieving embedding from Qdrant: {str(e)}")
            raise Exception(f"Error retrieving embedding: {str(e)}")

    def verify_storage(self, vector_id: str) -> bool:
        """Verify that an embedding was successfully stored."""
        try:
            record = self.get_embedding(vector_id)
            return record is not None
        except:
            return False

    def count_vectors(self) -> int:
        """Count the number of vectors in the collection."""
        try:
            count = self.client.count(
                collection_name=self.collection_name
            )
            return count.count
        except Exception as e:
            raise Exception(f"Error counting vectors: {str(e)}")

    def health_check(self) -> bool:
        """Perform a health check on the Qdrant connection."""
        try:
            # Try to get collections to verify connection
            self.client.get_collections()
            return True
        except:
            return False