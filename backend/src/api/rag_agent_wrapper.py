"""
RAG Agent API Wrapper

This module provides a wrapper around the RAG agent to be used by the API endpoint.
It handles the import issues by creating a separate interface.
"""

import sys
import os
from typing import List, Optional, Dict, Any
import time
import uuid
from pydantic import BaseModel

# Add the rag agent directory to the Python path to allow imports
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
rag_agent_dir = os.path.join(base_dir, 'rag agent')

# Add rag agent directory to Python path
if rag_agent_dir not in sys.path:
    sys.path.insert(0, rag_agent_dir)

# Import the necessary modules using absolute imports within the rag agent structure
import importlib.util

# Load the settings module - need to handle environment variables properly

# First, load the dotenv to ensure environment variables are available
from dotenv import load_dotenv
load_dotenv(os.path.join(base_dir, "backend", ".env"))

settings_spec = importlib.util.spec_from_file_location("settings", os.path.join(rag_agent_dir, "config", "settings.py"))
settings_module = importlib.util.module_from_spec(settings_spec)

# Execute the settings module in a way that allows it to access environment variables
settings_spec.loader.exec_module(settings_module)
Settings = settings_module.Settings

# Load the models module
models_spec = importlib.util.spec_from_file_location("agent_query", os.path.join(rag_agent_dir, "models", "agent_query.py"))
models_module = importlib.util.module_from_spec(models_spec)
models_spec.loader.exec_module(models_module)
AgentResponse = models_module.AgentResponse
AgentQuery = models_module.AgentQuery
RetrievedChunk = models_module.RetrievedChunk

# Create a simplified RAG agent implementation that doesn't rely on relative imports
class SimplifiedRAGAgent:
    """
    Simplified RAG agent that avoids the relative import issues in the original implementation.
    """
    def __init__(self):
        self.settings = Settings.load_from_env()

        # Initialize clients directly without relying on relative imports
        import cohere
        import google.generativeai as genai
        import os

        # Get Cohere model from environment, default to multilingual model
        self.cohere_model = os.getenv("COHERE_MODEL", "embed-multilingual-v2.0")

        self.cohere_client = cohere.Client(self.settings.cohere_api_key)
        genai.configure(api_key=self.settings.gemini_api_key)
        self.gemini_client = genai.GenerativeModel(self.settings.gemini_model)

        # Import Qdrant client
        from qdrant_client import QdrantClient
        from qdrant_client.http import models

        self.qdrant_client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            prefer_grpc=False
        )
        self.qdrant_collection_name = self.settings.qdrant_collection_name

    def process_query(self, agent_query: AgentQuery) -> AgentResponse:
        """
        Process a query using the simplified RAG approach.
        """
        try:
            # Generate embedding for the query using Cohere
            try:
                response = self.cohere_client.embed(
                    texts=[agent_query.text.strip()],
                    model=self.cohere_model,
                    input_type="search_query"
                )
            except Exception as e:
                print(f"Cohere embedding error: {str(e)}")
                return AgentResponse(
                    response_id=str(uuid.uuid4()),
                    query_id=agent_query.query_id,
                    content="I'm having trouble understanding your query due to API connection issues. Please check API keys.",
                    retrieved_chunks=[],
                    confidence_score=0.0
                )

            query_vector = response.embeddings[0] if response.embeddings and len(response.embeddings) > 0 else None

            if not query_vector:
                return AgentResponse(
                    response_id=str(uuid.uuid4()),
                    query_id=agent_query.query_id,
                    content="I'm having trouble understanding your query. Please try rephrasing.",
                    retrieved_chunks=[],
                    confidence_score=0.0
                )

            # Search in Qdrant for similar content
            search_result = self.qdrant_client.search(
                collection_name=self.qdrant_collection_name,
                query_vector=query_vector,
                limit=self.settings.max_chunks,
                score_threshold=self.settings.similarity_threshold
            )

            # Convert search results to RetrievedChunk objects
            retrieved_chunks = []
            for hit in search_result:
                if hasattr(hit, 'payload') and hasattr(hit, 'score'):
                    chunk = RetrievedChunk(
                        content=hit.payload.get('content', ''),
                        source=hit.payload.get('source', ''),
                        similarity_score=hit.score
                    )
                    retrieved_chunks.append(chunk)

            # Generate response using Gemini
            context_text = "\n".join([chunk.content for chunk in retrieved_chunks])
            prompt = f"""
            Context: {context_text}

            Question: {agent_query.text}

            Please provide a helpful answer based on the context. If the context doesn't contain relevant information, please say so.
            """

            gemini_response = self.gemini_client.generate_content(prompt)
            response_text = gemini_response.text if gemini_response.text else "I couldn't find relevant information to answer your question."

            # Calculate a basic confidence score based on similarity scores
            confidence_score = 0.0
            if retrieved_chunks:
                avg_similarity = sum(chunk.similarity_score for chunk in retrieved_chunks) / len(retrieved_chunks)
                confidence_score = min(avg_similarity, 1.0)  # Cap at 1.0

            return AgentResponse(
                response_id=str(uuid.uuid4()),
                query_id=agent_query.query_id,
                content=response_text,
                retrieved_chunks=retrieved_chunks,
                confidence_score=confidence_score
            )

        except Exception as e:
            print(f"Error in process_query: {str(e)}")
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                query_id=agent_query.query_id,
                content="I encountered an error while processing your query. Please try again later.",
                retrieved_chunks=[],
                confidence_score=0.0
            )

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the RAG agent and its dependencies.
        """
        try:
            # Test Cohere connection
            cohere_connected = True
            try:
                self.cohere_client.embed(
                    texts=["test"],
                    model="embed-english-v3.0"
                )
            except:
                cohere_connected = False

            # Test Qdrant connection
            qdrant_connected = True
            try:
                self.qdrant_client.get_collection(self.qdrant_collection_name)
            except:
                qdrant_connected = False

            # Test Gemini connection
            gemini_connected = True
            try:
                self.gemini_client.generate_content("Say hello")
            except:
                gemini_connected = False

            return {
                "qdrant_connected": qdrant_connected,
                "gemini_connected": gemini_connected,
                "cohere_connected": cohere_connected
            }
        except Exception as e:
            return {
                "qdrant_connected": False,
                "gemini_connected": False,
                "cohere_connected": False,
                "error": str(e)
            }

# Create a global instance
simplified_rag_agent = SimplifiedRAGAgent()


class RAGQueryRequest(BaseModel):
    query_text: str
    metadata: Optional[Dict[str, Any]] = None


class RetrievedChunkModel(BaseModel):
    content: str
    source: str
    similarity_score: float


class RAGQueryResponse(BaseModel):
    response_id: str
    query_id: str
    content: str
    retrieved_chunks: List[RetrievedChunkModel]
    confidence_score: float
    execution_time_ms: float


def process_rag_query(query_text: str) -> RAGQueryResponse:
    """
    Process a RAG query using the simplified RAG agent.
    """
    start_time = time.time()
    query_id = str(uuid.uuid4())
    response_id = str(uuid.uuid4())

    # Create AgentQuery object
    agent_query = AgentQuery(
        query_id=query_id,
        text=query_text,
        timestamp=time.time()
    )

    # Process the query using the simplified RAG agent
    agent_response: AgentResponse = simplified_rag_agent.process_query(agent_query)

    # Convert retrieved chunks to the API response format
    retrieved_chunks = [
        RetrievedChunkModel(
            content=chunk.content,
            source=chunk.source,
            similarity_score=chunk.similarity_score
        )
        for chunk in agent_response.retrieved_chunks
    ]

    execution_time_ms = (time.time() - start_time) * 1000

    # Create and return the API response
    api_response = RAGQueryResponse(
        response_id=response_id,
        query_id=query_id,
        content=agent_response.content,
        retrieved_chunks=retrieved_chunks,
        confidence_score=agent_response.confidence_score,
        execution_time_ms=execution_time_ms
    )

    return api_response


def check_rag_health() -> Dict[str, Any]:
    """
    Check the health of the RAG agent and its dependencies.
    """
    try:
        health_status = simplified_rag_agent.health_check()

        all_connected = all([
            health_status.get("qdrant_connected", False),
            health_status.get("gemini_connected", False),
            health_status.get("cohere_connected", False)
        ])

        return {
            "status": "healthy" if all_connected else "unhealthy",
            "qdrant_connected": health_status.get("qdrant_connected", False),
            "gemini_connected": health_status.get("gemini_connected", False),
            "cohere_connected": health_status.get("cohere_connected", False)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }