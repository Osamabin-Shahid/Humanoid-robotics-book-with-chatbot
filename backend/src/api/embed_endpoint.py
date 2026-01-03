"""
Embed Endpoint

This module implements the embed API endpoint
for the RAG URL ingestion pipeline.
"""

from typing import Dict, Any
import traceback
from fastapi import APIRouter, HTTPException, status
from src.api.models import EmbeddingRequest, EmbeddingResponse, ErrorResponse
from src.config.settings import Settings
from src.services.embedding_service import EmbeddingService
from src.models.chunk_model import TextChunk


router = APIRouter()


@router.post("/api/v1/embed", response_model=EmbeddingResponse)
async def embed_endpoint(request: EmbeddingRequest) -> EmbeddingResponse:
    """
    Generate embeddings for provided text chunks.

    Args:
        request: EmbeddingRequest containing text chunks and model

    Returns:
        EmbeddingResponse with generated embeddings
    """
    try:
        # Load settings
        settings = Settings()

        # Initialize embedding service
        embedding_service = EmbeddingService(settings)

        # Create TextChunk objects from the request
        chunks = []
        for chunk_data in request.chunks:
            chunk = TextChunk(
                chunk_id=chunk_data['chunk_id'],
                content=chunk_data['content'],
                source_url=chunk_data.get('source_url', ''),
                section=chunk_data.get('section', ''),
                sequence_number=chunk_data.get('sequence_number', 0),
                token_count=chunk_data.get('token_count', 0)
            )
            chunks.append(chunk)

        # Generate embeddings
        embeddings = embedding_service.generate_embeddings_for_chunks(
            chunks,
            request.model
        )

        # Convert embeddings to response format
        embedding_data = []
        for embedding in embeddings:
            embedding_data.append({
                'chunk_id': embedding.source_chunk_id,
                'vector': embedding.vector_data,
                'model': embedding.model_name,
                'dimension': embedding.dimension
            })

        # Create response
        response = EmbeddingResponse(
            embeddings=embedding_data,
            model=request.model or settings.cohere_model,
            total_processed=len(chunks)
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