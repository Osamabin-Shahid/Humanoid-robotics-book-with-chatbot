"""
Crawl Endpoint

This module implements the crawl API endpoint
for the RAG URL ingestion pipeline.
"""

from typing import Dict, Any
import traceback
from fastapi import APIRouter, HTTPException, status
from src.api.models import CrawlRequest, CrawlResponse, ErrorResponse
from src.config.settings import Settings
from src.services.crawling_service import CrawlingService


router = APIRouter()


@router.post("/api/v1/crawl", response_model=CrawlResponse)
async def crawl_endpoint(request: CrawlRequest) -> CrawlResponse:
    """
    Initiate a website crawling and ingestion operation.

    Args:
        request: CrawlRequest containing URLs and configuration

    Returns:
        CrawlResponse with crawl results
    """
    try:
        # Load settings
        settings = Settings()

        # Extract configuration
        config = request.configuration or {}
        chunk_size = config.get('chunk_size', settings.chunk_size)
        overlap_percentage = config.get('overlap_percentage', settings.overlap_percentage)

        # Initialize crawling service
        crawling_service = CrawlingService(settings)

        # Process the URLs
        result = crawling_service.process_urls(
            urls=request.urls,
            chunk_size=chunk_size,
            overlap_percentage=overlap_percentage
        )

        # Convert to response format
        response = CrawlResponse(
            crawl_id=result.crawl_id,
            status=result.status,
            pages_processed=result.pages_processed,
            total_chunks=result.total_chunks,
            error_count=result.error_count,
            start_time=result.start_time.isoformat(),
            end_time=result.end_time.isoformat(),
            processed_urls=result.processed_urls,
            error_details=result.error_details
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/api/v1/crawl/incremental", response_model=CrawlResponse)
async def crawl_incremental_endpoint(request: CrawlRequest) -> CrawlResponse:
    """
    Initiate an incremental website crawling and ingestion operation.

    Args:
        request: CrawlRequest containing URLs and configuration

    Returns:
        CrawlResponse with incremental crawl results
    """
    try:
        # Load settings
        settings = Settings()

        # Extract configuration
        config = request.configuration or {}
        chunk_size = config.get('chunk_size', settings.chunk_size)
        overlap_percentage = config.get('overlap_percentage', settings.overlap_percentage)

        # Initialize crawling service
        crawling_service = CrawlingService(settings)

        # Process the URLs incrementally (for now, just use the incremental method)
        # In a real implementation, you'd need to pass existing chunks for comparison
        result = crawling_service.process_urls_incremental(
            urls=request.urls,
            chunk_size=chunk_size,
            overlap_percentage=overlap_percentage
        )

        # Convert to response format
        response = CrawlResponse(
            crawl_id=result.crawl_id,
            status=result.status,
            pages_processed=result.pages_processed,
            total_chunks=result.total_chunks,
            error_count=result.error_count,
            start_time=result.start_time.isoformat(),
            end_time=result.end_time.isoformat(),
            processed_urls=result.processed_urls,
            error_details=result.error_details
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )