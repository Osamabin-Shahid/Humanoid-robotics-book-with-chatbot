"""
RAG Agent API Endpoint

This module creates the API endpoint for the RAG agent functionality,
exposing the RAG agent as an HTTP API endpoint that can be called from the frontend.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from .rag_agent_wrapper import process_rag_query, check_rag_health, RAGQueryRequest, RAGQueryResponse, RetrievedChunkModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag-agent", tags=["rag-agent"])


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag_agent(request: RAGQueryRequest):
    """
    Submit a query to the RAG agent and receive a response based on retrieved content.
    """
    try:
        # Process the query using the RAG agent wrapper
        result = process_rag_query(request.query_text)

        logger.info(f"Successfully processed query {result.query_id} in {result.execution_time_ms:.2f}ms")
        return result

    except Exception as e:
        logger.error(f"Error processing RAG agent query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health")
async def rag_agent_health():
    """
    Check the health of the RAG agent and its dependencies.
    """
    try:
        health_status = check_rag_health()
        return health_status
    except Exception as e:
        logger.error(f"RAG agent health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }