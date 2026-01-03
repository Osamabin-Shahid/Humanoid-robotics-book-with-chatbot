#!/usr/bin/env python3
"""
RAG URL Pipeline - Main Entry Point

This script provides the main entry point for the RAG URL ingestion pipeline
that crawls deployed book websites, extracts clean text, generates embeddings,
and stores them in Qdrant Cloud.
"""

import argparse
import sys
import logging
from src.services.crawling_service import CrawlingService
from src.services.embedding_service import EmbeddingService
from src.services.storage_service import StorageService
from src.config.settings import Settings
from src.models.chunk_model import TextChunk


def setup_logging():
    """Set up logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point for the RAG URL ingestion pipeline."""
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="RAG URL Ingestion Pipeline")
    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="List of website URLs to process"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Size of text chunks in tokens (default: 512)"
    )
    parser.add_argument(
        "--overlap",
        type=float,
        default=0.2,
        help="Overlap percentage between chunks (default: 0.2)"
    )
    parser.add_argument(
        "--store",
        action="store_true",
        help="Store embeddings in Qdrant (default: False)"
    )

    args = parser.parse_args()

    # Load settings
    settings = Settings()

    # Initialize services
    crawling_service = CrawlingService(settings)
    embedding_service = EmbeddingService(settings)
    storage_service = StorageService(settings) if args.store else None

    try:
        logger.info(f"Starting ingestion pipeline for URLs: {args.urls}")

        # Process URLs and get text chunks
        crawl_result, text_chunks = crawling_service.process_urls_with_chunks(
            urls=args.urls,
            chunk_size=args.chunk_size,
            overlap_percentage=args.overlap
        )
        logger.info(f"Crawling completed: Status={crawl_result.status}, Pages={crawl_result.pages_processed}, Chunks={crawl_result.total_chunks}")

        if crawl_result.total_chunks == 0:
            logger.warning("No chunks were generated from the provided URLs")
            return

        # Generate embeddings for the text chunks
        logger.info("Generating embeddings for text chunks...")
        embeddings = embedding_service.generate_embeddings_for_chunks(
            text_chunks,
            model=settings.cohere_model
        )
        logger.info(f"Embedding generation completed for {len(text_chunks)} chunks")

        if storage_service and args.store:
            logger.info("Initializing storage...")
            storage_service.initialize_storage()
            logger.info("Storing embeddings in Qdrant...")
            storage_result = storage_service.store_embeddings_with_retry(
                embeddings,
                text_chunks
            )
            logger.info(f"Storage completed: {storage_result.message}")

        logger.info("Pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()