#!/usr/bin/env python3
"""
Debug script to test Qdrant storage with detailed error information
"""
import logging
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient
from src.embedding.generator import EmbeddingGenerator
from src.crawler.website_crawler import WebsiteCrawler
from src.chunking.text_chunker import TextChunker
from src.models.chunk_model import TextChunk

def debug_storage():
    """Debug the storage process step by step."""
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
            from src.storage.models import Metadata
            from datetime import datetime

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

            logger.info("Attempting to store test embedding...")
            result = client.store_embedding(embeddings[0], metadata)
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
    debug_storage()