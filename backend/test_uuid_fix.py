#!/usr/bin/env python3
"""
Test script to verify Qdrant storage with proper UUID format
"""
import logging
import uuid
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient
from src.embedding.generator import EmbeddingGenerator
from src.models.chunk_model import TextChunk
from src.storage.models import Metadata
from datetime import datetime

def test_with_proper_uuid():
    """Test the storage process with proper UUID format."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    settings = Settings()

    # Test Qdrant connection first
    logger.info("Testing Qdrant connection...")
    client = QdrantCloudClient(settings)

    try:
        is_healthy = client.health_check()
        logger.info(f"Qdrant health check: {is_healthy}")

        # Try to create collection
        logger.info("Creating collection...")
        result = client.create_collection()
        logger.info(f"Collection creation result: {result}")

        # Count vectors before
        count_before = client.count_vectors()
        logger.info(f"Vector count before test: {count_before}")

        # Create a test embedding to store
        logger.info("Creating test embedding...")
        generator = EmbeddingGenerator(settings)

        # Generate a simple test embedding
        test_text = "This is a test document for debugging purposes."
        embeddings = generator.generate_embeddings([test_text])
        logger.info(f"Generated {len(embeddings)} embeddings")

        if embeddings:
            # Create test metadata
            metadata = Metadata(
                chunk_id="test_chunk_1",
                source_url="https://test.com",
                section="test",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                content_hash="test_hash",
                token_count=10
            )
            metadata.validate()

            # Create a new embedding with a proper UUID
            proper_uuid = str(uuid.uuid4())
            logger.info(f"Using proper UUID: {proper_uuid}")

            # Update the embedding vector_id to use proper UUID
            from src.embedding.models import EmbeddingVector
            proper_embedding = EmbeddingVector(
                vector_id=proper_uuid,
                vector_data=embeddings[0].vector_data,
                model_name=embeddings[0].model_name,
                model_version=embeddings[0].model_version,
                dimension=embeddings[0].dimension,
                source_chunk_id=embeddings[0].source_chunk_id
            )

            logger.info("Attempting to store test embedding with proper UUID...")
            result = client.store_embedding(proper_embedding, metadata)
            logger.info(f"Storage result: {result}")

            # Count vectors after
            count_after = client.count_vectors()
            logger.info(f"Vector count after test: {count_after}")

            if count_after > count_before:
                logger.info("SUCCESS: Test embedding was stored in Qdrant!")
            else:
                logger.info("FAILED: Test embedding was not stored in Qdrant")

    except Exception as e:
        logger.error(f"Error during storage test: {e}", exc_info=True)

if __name__ == "__main__":
    test_with_proper_uuid()