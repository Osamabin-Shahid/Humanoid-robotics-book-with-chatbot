import cohere
from typing import List, Optional
import logging
from ..models.agent_query import AgentQuery, RetrievedChunk, AgentResponse
from ..retrieval.qdrant_client import qdrant_client
from ..services.response_generator import response_generator
from ..services.logging_service import logging_service, LogOperationType
from ..config.settings import settings


class RAGAgent:
    """
    Core RAG agent that orchestrates query processing and response generation.
    Integrates query understanding, retrieval, and response generation.
    """

    def __init__(self):
        """
        Initialize the RAG agent with required services.
        """
        # Initialize Cohere client for query embedding
        # Note: We're using Cohere for query embedding to match the stored embeddings
        self.cohere_client = cohere.Client(settings.cohere_api_key)

    def process_query(self, query_text: str) -> AgentResponse:
        """
        Process a user query and return a grounded response.

        Args:
            query_text: The natural language query from the user

        Returns:
            AgentResponse object containing the generated response
        """
        # Create an AgentQuery object
        agent_query = AgentQuery.create(text=query_text)

        # Log the query
        logging_service.log_query(
            query_id=agent_query.query_id,
            query_text=agent_query.text
        )

        try:
            # Step 1: Generate embedding for the query
            query_vector = self._generate_query_embedding(query_text)

            if query_vector is None:
                # If embedding generation failed, return an error response
                error_response = AgentResponse.create(
                    query_id=agent_query.query_id,
                    content="I'm having trouble understanding your query. Please try rephrasing.",
                    retrieved_chunks=[],
                    confidence_score=0.0
                )
                return error_response

            # Step 2: Retrieve relevant chunks from Qdrant
            start_time = __import__('time').time()
            retrieved_chunks = qdrant_client.retrieve_chunks(
                query_vector=query_vector,
                limit=settings.max_chunks_to_retrieve,
                similarity_threshold=settings.similarity_threshold
            )
            retrieval_time = (__import__('time').time() - start_time) * 1000  # Convert to milliseconds

            # Log the retrieval
            logging_service.log_retrieval(
                query_id=agent_query.query_id,
                num_chunks_retrieved=len(retrieved_chunks),
                retrieval_time_ms=retrieval_time,
                similarity_threshold=settings.similarity_threshold
            )

            # Step 3: Generate response using the retrieved chunks
            agent_response = response_generator.generate_response(
                query_text=query_text,
                retrieved_chunks=retrieved_chunks,
                query_id=agent_query.query_id
            )

            # Step 4: Validate that the response is grounded in the retrieved content
            validation_result = response_generator.validate_response_grounding(
                response=agent_response.content,
                retrieved_chunks=agent_response.retrieved_chunks
            )

            # Log the validation
            logging_service.log_validation(
                query_id=agent_query.query_id,
                response_id=agent_response.response_id,
                is_valid=validation_result["is_valid"],
                validation_details=validation_result["details"]
            )

            return agent_response

        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            logging_service.log_error(
                error=e,
                operation_context="query_processing",
                query_id=agent_query.query_id
            )

            # Return an error response
            error_response = AgentResponse.create(
                query_id=agent_query.query_id,
                content="I encountered an error while processing your query. Please try again later.",
                retrieved_chunks=[],
                confidence_score=0.0
            )
            return error_response

    def _generate_query_embedding(self, query_text: str) -> Optional[List[float]]:
        """
        Generate an embedding vector for the query text using Cohere.
        This matches the embedding model used for the stored content in Qdrant.

        Args:
            query_text: The query text to embed

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        try:
            # Validate input
            if not query_text or not query_text.strip():
                logging.error("Query text is empty or None")
                return None

            # Use Cohere to generate embedding for the query
            # This matches the embedding model used for the stored content
            response = self.cohere_client.embed(
                texts=[query_text.strip()],
                model="embed-english-v3.0"  # Using a common Cohere embedding model
            )

            # Extract the embedding from the response
            if response and hasattr(response, 'embeddings') and response.embeddings and len(response.embeddings) > 0:
                return response.embeddings[0]
            else:
                logging.error("No embeddings returned from Cohere")
                return None

        except Exception as e:
            logging.error(f"Error generating query embedding: {str(e)}")
            # If Cohere fails, we could potentially use a fallback method
            # For now, we'll return None which will cause the query to fail gracefully
            return None

    def check_health(self) -> dict:
        """
        Check the health of the RAG agent and its dependencies.

        Returns:
            Dictionary with health status information
        """
        health_status = {
            "rag_agent": True,
            "qdrant_connected": False,
            "response_generator_available": True,
            "configuration_valid": True,
            "details": {}
        }

        try:
            # Validate configuration first
            if not settings.qdrant_url or not settings.qdrant_api_key:
                health_status["configuration_valid"] = False
                health_status["details"]["configuration_error"] = "Missing Qdrant configuration"

            if not settings.gemini_api_key:
                health_status["response_generator_available"] = False
                health_status["details"]["api_error"] = "Missing Gemini API key"

            if not settings.cohere_api_key:
                health_status["details"]["api_error"] = "Missing Cohere API key (required for embeddings)"

            # Only check Qdrant connection if configuration is valid
            if health_status["configuration_valid"]:
                qdrant_healthy = qdrant_client.check_connection()
                health_status["qdrant_connected"] = qdrant_healthy
                health_status["details"]["qdrant"] = qdrant_healthy

                # Log health check
                logging_service.log_health_check(
                    service_name="qdrant",
                    is_healthy=qdrant_healthy
                )
        except Exception as e:
            logging.error(f"Error checking Qdrant health: {str(e)}")
            health_status["qdrant_connected"] = False
            health_status["details"]["qdrant_error"] = str(e)

        return health_status


# Global RAG agent instance
rag_agent = RAGAgent()