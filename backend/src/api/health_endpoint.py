"""
Health Endpoint

This module implements the health check API endpoint
for the RAG URL ingestion pipeline.
"""

from typing import Dict, Any
import datetime
from fastapi import APIRouter, status
from src.api.models import HealthResponse, ErrorResponse
from src.config.settings import Settings
from src.services.storage_service import StorageService


router = APIRouter()


@router.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check the health status of the service.

    Returns:
        HealthResponse with service status
    """
    try:
        # Load settings
        settings = Settings()

        # Initialize storage service for health check
        storage_service = StorageService(settings)

        # Check if we can connect to Qdrant
        is_healthy = storage_service.health_check()

        status_str = "healthy" if is_healthy else "unhealthy"

        # Create response
        response = HealthResponse(
            status=status_str,
            timestamp=datetime.datetime.now().isoformat(),
            version="1.0.0"
        )

        return response

    except Exception as e:
        # If there's an error during health check, return unhealthy
        response = HealthResponse(
            status="unhealthy",
            timestamp=datetime.datetime.now().isoformat(),
            version="1.0.0"
        )
        return response


@router.get("/api/v1/ready", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """
    Check the readiness of the service.

    Returns:
        HealthResponse with service readiness status
    """
    try:
        # Load settings
        settings = Settings()

        # Check if all required configuration is available
        required_settings = [
            settings.cohere_api_key,
            settings.qdrant_url
        ]

        if not all(required_settings):
            status_str = "unready"
        else:
            # Initialize storage service for readiness check
            storage_service = StorageService(settings)

            # Check if we can connect to Qdrant
            is_ready = storage_service.health_check()
            status_str = "ready" if is_ready else "unready"

        # Create response
        response = HealthResponse(
            status=status_str,
            timestamp=datetime.datetime.now().isoformat(),
            version="1.0.0"
        )

        return response

    except Exception:
        # If there's an error during readiness check, return unready
        response = HealthResponse(
            status="unready",
            timestamp=datetime.datetime.now().isoformat(),
            version="1.0.0"
        )
        return response