#!/usr/bin/env python3
"""
Test Qdrant connection stability
"""
import logging
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient

def test_connection_stability():
    """Test basic Qdrant connection without storing."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    settings = Settings()
    client = QdrantCloudClient(settings)

    try:
        # Test basic health
        is_healthy = client.health_check()
        logger.info(f"Health check: {is_healthy}")

        # Test collection info
        collections = client.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        logger.info(f"Available collections: {collection_names}")

        # Test count
        count = client.count_vectors()
        logger.info(f"Vector count: {count}")

        # Test if collection exists
        if settings.qdrant_collection_name in collection_names:
            logger.info(f"Collection '{settings.qdrant_collection_name}' exists")

            # Get collection info
            collection_info = client.client.get_collection(settings.qdrant_collection_name)
            logger.info(f"Collection vectors count: {collection_info.points_count}")
            logger.info(f"Collection config: {collection_info.config}")
        else:
            logger.info(f"Collection '{settings.qdrant_collection_name}' does not exist")

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection_stability()