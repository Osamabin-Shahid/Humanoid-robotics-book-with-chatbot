#!/usr/bin/env python3
"""
Script to verify actual data in Qdrant collection
"""
import os
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient

def verify_actual_data():
    """Verify the actual data in Qdrant collection."""
    settings = Settings()
    client = QdrantCloudClient(settings)

    try:
        # Get collection info
        print(f"Collection name: {settings.qdrant_collection_name}")

        # Count vectors
        count = client.count_vectors()
        print(f"Total vector count: {count}")

        # Try to list all points if count is small
        if count <= 10:
            print("Attempting to retrieve points...")
            try:
                # Use scroll to get points
                from qdrant_client.http import models
                records, next_page = client.client.scroll(
                    collection_name=settings.qdrant_collection_name,
                    limit=10
                )

                print(f"Retrieved {len(records)} records:")
                for i, record in enumerate(records):
                    print(f"  Record {i+1}:")
                    print(f"    ID: {record.id}")
                    print(f"    Payload keys: {list(record.payload.keys()) if record.payload else 'None'}")
                    print(f"    Source URL: {record.payload.get('source_url', 'N/A') if record.payload else 'N/A'}")
                    print(f"    Vector length: {len(record.vector) if record.vector else 0}")

            except Exception as e:
                print(f"Could not retrieve records via scroll: {e}")
        else:
            print(f"Collection has {count} vectors, skipping detailed listing")

        # Try health check
        is_healthy = client.health_check()
        print(f"Health status: {'Healthy' if is_healthy else 'Unhealthy'}")

    except Exception as e:
        print(f"Error verifying data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_actual_data()