#!/usr/bin/env python3
"""
Script to check Qdrant collection status
"""
import os
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient

def check_qdrant_status():
    """Check the status of the Qdrant collection."""
    settings = Settings()
    client = QdrantCloudClient(settings)

    try:
        # Check if collection exists and get vector count
        count = client.count_vectors()
        print(f"Vector count in collection '{settings.qdrant_collection_name}': {count}")

        # Perform health check
        is_healthy = client.health_check()
        print(f"Qdrant health status: {'Healthy' if is_healthy else 'Unhealthy'}")

        # Try to get some vectors if they exist
        if count > 0:
            print(f"Collection contains {count} vectors")
            # Try to get the first few vectors to verify content
            try:
                # Search for similar vectors (using a dummy query)
                dummy_vector = [0.0] * 768  # Cohere vector size
                results = client.search_similar(dummy_vector, limit=1)
                if results:
                    print(f"Sample result: ID={results[0]['id']}, Score={results[0]['score']}")
                    print(f"Sample payload keys: {list(results[0]['payload'].keys())}")
            except Exception as e:
                print(f"Could not retrieve sample vectors: {e}")
        else:
            print("Collection is empty")

    except Exception as e:
        print(f"Error checking Qdrant status: {e}")

if __name__ == "__main__":
    check_qdrant_status()