#!/usr/bin/env python3
"""
Test script to debug Qdrant storage issues
"""
import logging
import uuid
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient
from src.embedding.generator import EmbeddingGenerator
from src.storage.models import Metadata
from datetime import datetime

def debug_storage_issue():
    """Debug the specific storage issue with Qdrant."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    settings = Settings()
    client = QdrantCloudClient(settings)

    try:
        # Generate a real embedding
        generator = EmbeddingGenerator(settings)
        test_text = "Physical AI and Humanoid Robotics: Advanced concepts in embodied artificial intelligence."
        embeddings = generator.generate_embeddings([test_text])

        if embeddings:
            logger.info(f"Generated embedding with vector length: {len(embeddings[0].vector_data)}")
            logger.info(f"Vector ID format: {embeddings[0].vector_id}")
            logger.info(f"Vector ID type: {type(embeddings[0].vector_id)}")

            # Create metadata
            metadata = Metadata(
                chunk_id="test_chunk_real",
                source_url="https://physical-ai-and-humanoid-robotics-rho.vercel.app/docs/intro",
                section="test",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                content_hash="real_content_hash",
                token_count=15
            )
            metadata.validate()

            # Test with a proper UUID
            proper_uuid = str(uuid.uuid4())
            logger.info(f"Testing with proper UUID: {proper_uuid}")

            from src.embedding.models import EmbeddingVector
            proper_embedding = EmbeddingVector(
                vector_id=proper_uuid,
                vector_data=embeddings[0].vector_data,
                model_name=embeddings[0].model_name,
                model_version=embeddings[0].model_version,
                dimension=embeddings[0].dimension,
                source_chunk_id=embeddings[0].source_chunk_id
            )

            # Try to store with proper UUID
            logger.info("Attempting to store with proper UUID...")
            result = client.store_embedding(proper_embedding, metadata)
            logger.info(f"Storage result with UUID: {result}")

            # Count vectors after
            count_after = client.count_vectors()
            logger.info(f"Vector count after UUID test: {count_after}")

    except Exception as e:
        logger.error(f"Error in UUID test: {e}", exc_info=True)

        # Try with integer ID instead
        try:
            from src.embedding.models import EmbeddingVector
            import random
            int_id = random.randint(100000, 999999)
            logger.info(f"Trying with integer ID: {int_id}")

            int_embedding = EmbeddingVector(
                vector_id=str(int_id),  # Qdrant might accept string of integer
                vector_data=embeddings[0].vector_data,
                model_name=embeddings[0].model_name,
                model_version=embeddings[0].model_version,
                dimension=embeddings[0].dimension,
                source_chunk_id=embeddings[0].source_chunk_id
            )

            logger.info("Attempting to store with integer ID...")
            result = client.store_embedding(int_embedding, metadata)
            logger.info(f"Storage result with int ID: {result}")

        except Exception as e2:
            logger.error(f"Error with integer ID too: {e2}", exc_info=True)

if __name__ == "__main__":
    debug_storage_issue()