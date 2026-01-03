#!/usr/bin/env python3
"""
Test to verify if the issue is with embedding vector storage
"""
import logging
import uuid
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient
from src.embedding.generator import EmbeddingGenerator
from src.storage.models import Metadata
from datetime import datetime

def test_real_embedding_with_proper_uuid():
    """Test storing a real embedding with proper UUID."""
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
            logger.info(f"Original vector ID: {embeddings[0].vector_id}")

            # Create proper UUID
            proper_uuid = str(uuid.uuid4())
            logger.info(f"Using proper UUID: {proper_uuid}")

            # Create proper embedding with UUID
            from src.embedding.models import EmbeddingVector
            proper_embedding = EmbeddingVector(
                vector_id=proper_uuid,
                vector_data=embeddings[0].vector_data,
                model_name=embeddings[0].model_name,
                model_version=embeddings[0].model_version,
                dimension=embeddings[0].dimension,
                source_chunk_id=embeddings[0].source_chunk_id
            )

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

            # Try to store
            logger.info("Attempting to store real embedding with proper UUID...")
            result = client.store_embedding(proper_embedding, metadata)
            logger.info(f"Storage result: {result}")

            # Count vectors after
            count_after = client.count_vectors()
            logger.info(f"Total vector count: {count_after}")

            # Verify by searching
            results = client.search_similar(embeddings[0].vector_data[:100], limit=1)  # Use first 100 dims for test
            logger.info(f"Search results: {len(results)}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    test_real_embedding_with_proper_uuid()