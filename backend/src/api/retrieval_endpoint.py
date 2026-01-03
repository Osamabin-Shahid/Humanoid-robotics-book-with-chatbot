"""
Retrieval API Endpoint

This module provides FastAPI endpoints for the RAG retrieval functionality.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.models.retrieval_result_model import RetrievalResult


# Initialize FastAPI router
router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalRequest(BaseModel):
    """
    Request model for retrieval endpoint.
    """
    query_text: str
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return")
    min_score: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity score threshold")
    validate_results: bool = Query(False, description="Whether to validate results before returning")


class RetrievalResponse(BaseModel):
    """
    Response model for retrieval endpoint.
    """
    query_id: str
    query_text: str
    results: List[RetrievalResult]
    total_results: int
    execution_time_ms: float


class ValidationRequest(BaseModel):
    """
    Request model for validation endpoint.
    """
    query_text: str
    expected_keywords: List[str]
    limit: int = Query(10, ge=1, le=100, description="Number of results to validate")


class ValidationResponse(BaseModel):
    """
    Response model for validation endpoint.
    """
    validation_report: dict
    is_valid: bool
    issues_found: List[str]


def get_settings():
    """
    Dependency to get settings instance.
    """
    return Settings()


def get_retrieval_service():
    """
    Dependency to get retrieval service instance.
    """
    settings = get_settings()
    return RetrievalService(settings)


@router.post("/retrieve", response_model=RetrievalResponse, summary="Retrieve relevant content")
async def retrieve_content(
    request: RetrievalRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Retrieve relevant content from the vector database based on the query text.

    Args:
        request: The retrieval request containing query and parameters
        retrieval_service: The retrieval service instance

    Returns:
        RetrievalResponse: The retrieval results
    """
    try:
        import time
        start_time = time.time()

        # Perform retrieval based on validation preference
        if request.validate_results:
            results = retrieval_service.retrieve_and_validate(
                query_text=request.query_text,
                limit=request.limit,
                min_score=request.min_score
            )
        else:
            results = retrieval_service.retrieve(
                query_text=request.query_text,
                limit=request.limit,
                min_score=request.min_score
            )

        execution_time_ms = (time.time() - start_time) * 1000

        # Create response
        response = RetrievalResponse(
            query_id=f"api_query_{int(time.time())}",
            query_text=request.query_text,
            results=results,
            total_results=len(results),
            execution_time_ms=round(execution_time_ms, 2)
        )

        logger.info(f"Retrieved {len(results)} results for query: {request.query_text[:50]}...")
        return response

    except Exception as e:
        logger.error(f"Error during retrieval: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.post("/retrieve-with-validation", response_model=dict, summary="Retrieve and validate content")
async def retrieve_with_validation(
    request: RetrievalRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Retrieve relevant content and return both results and validation reports.

    Args:
        request: The retrieval request containing query and parameters
        retrieval_service: The retrieval service instance

    Returns:
        dict: Results and validation reports
    """
    try:
        import time
        start_time = time.time()

        # Perform retrieval with validation reports
        result = retrieval_service.retrieve_with_validation_reports(
            query_text=request.query_text,
            limit=request.limit,
            min_score=request.min_score
        )

        execution_time_ms = (time.time() - start_time) * 1000
        result["execution_time_ms"] = round(execution_time_ms, 2)

        logger.info(f"Retrieved with validation {len(result['results'])} results for query: {request.query_text[:50]}...")
        return result

    except Exception as e:
        logger.error(f"Error during retrieval with validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval with validation failed: {str(e)}")


@router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Health check endpoint to verify the service is running.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "RAG Retrieval API",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }


# Additional utility endpoints
@router.get("/query/{query_id}", summary="Get query results by ID")
async def get_query_results(
    query_id: str,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Retrieve results for a specific query ID (placeholder implementation).

    Args:
        query_id: The ID of the query to retrieve
        retrieval_service: The retrieval service instance

    Returns:
        dict: Query results
    """
    # This is a placeholder - in a real implementation, you would store and retrieve query results by ID
    return {
        "query_id": query_id,
        "message": "Query result retrieval by ID is not implemented in this version",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }