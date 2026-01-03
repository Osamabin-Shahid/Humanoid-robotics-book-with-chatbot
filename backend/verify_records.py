#!/usr/bin/env python3
"""
Script to verify actual data in Qdrant collection by retrieving records
"""
import logging
from src.config.settings import Settings
from src.storage.qdrant_client import QdrantCloudClient

def verify_actual_data():
    """Verify actual data in Qdrant collection by retrieving records."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    settings = Settings()
    client = QdrantCloudClient(settings)

    try:
        # Get collection info
        print(f"Collection name: {settings.qdrant_collection_name}")

        # Count vectors
        count = client.count_vectors()
        print(f"Total vector count: {count}")

        if count > 0:
            print(f"\nRetrieving sample records from collection...")

            # Use scroll to get actual records
            from qdrant_client.http import models
            try:
                # Try to get records using scroll
                records, next_page = client.client.scroll(
                    collection_name=settings.qdrant_collection_name,
                    limit=min(5, count)  # Get up to 5 records or total count if less
                )

                print(f"Retrieved {len(records)} sample records:")
                for i, record in enumerate(records):
                    print(f"\n  Record {i+1}:")
                    print(f"    ID: {record.id}")
                    print(f"    Vector length: {len(record.vector) if record.vector else 'N/A'}")
                    print(f"    Payload keys: {list(record.payload.keys()) if record.payload else 'None'}")
                    if record.payload:
                        print(f"    Source URL: {record.payload.get('source_url', 'N/A')}")
                        print(f"    Chunk ID: {record.payload.get('chunk_id', 'N/A')}")
                        print(f"    Section: {record.payload.get('section', 'N/A')}")
                        print(f"    Token count: {record.payload.get('token_count', 'N/A')}")

            except Exception as e:
                print(f"Could not retrieve records via scroll: {e}")
                print("This might indicate the data is not accessible or there's an API issue")

        else:
            print("Collection is empty")

        # Try health check
        is_healthy = client.health_check()
        print(f"\nHealth status: {'Healthy' if is_healthy else 'Unhealthy'}")

    except Exception as e:
        print(f"Error verifying data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_actual_data()