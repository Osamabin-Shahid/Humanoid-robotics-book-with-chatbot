"""
Main API Application

This module creates the FastAPI application for the RAG system, including both URL ingestion pipeline
and retrieval/validation functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.api.crawl_endpoint import router as crawl_router
from src.api.embed_endpoint import router as embed_router
from src.api.health_endpoint import router as health_router
from src.api.retrieval_endpoint import router as retrieval_router
from src.api.validation_endpoint import router as validation_router
from src.api.rag_agent_endpoint import router as rag_agent_router
from src.config.settings import Settings


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown.
    """
    # Startup
    logger.info("Starting RAG System API...")

    # Initialize settings to verify configuration
    try:
        settings = Settings()
        logger.info(f"API initialized with Qdrant collection: {settings.qdrant_collection_name}")
    except Exception as e:
        logger.error(f"Failed to initialize settings: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down RAG System API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="RAG System API",
        description="API for crawling websites, generating embeddings, storing in Qdrant, and retrieving/validating content",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, configure this properly
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(crawl_router)
    app.include_router(embed_router)
    app.include_router(health_router)

    # Include retrieval and validation routers for the new functionality
    app.include_router(
        retrieval_router,
        prefix="/api/v1/retrieval",
        tags=["retrieval"]
    )

    app.include_router(
        validation_router,
        prefix="/api/v1/validation",
        tags=["validation"]
    )

    # Include RAG agent router
    app.include_router(
        rag_agent_router,
        prefix="/api/v1",
        tags=["rag-agent"]
    )

    @app.get("/")
    async def root():
        """Root endpoint for the API."""
        return {
            "message": "RAG System API",
            "version": "1.0.0",
            "description": "API for crawling, embedding, storing, retrieving, and validating content",
            "endpoints": [
                "/api/v1/crawl",
                "/api/v1/embed",
                "/api/v1/health",
                "/api/v1/ready",
                "/api/v1/retrieval/",
                "/api/v1/validation/",
                "/api/v1/rag-agent/query",
                "/api/v1/rag-agent/health",
                "/docs",
                "/redoc"
            ]
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    import os

    # Get host and port from environment or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    # Run the application
    uvicorn.run(
        "main_api:app",
        host=host,
        port=port,
        reload=True,  # Set to False in production
        log_level="info"
    )