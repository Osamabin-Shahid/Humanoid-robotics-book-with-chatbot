import google.generativeai as genai
from typing import List, Optional
import logging
from ..models.agent_query import RetrievedChunk, AgentResponse
from ..config.settings import settings
from ..services.logging_service import logging_service, LogOperationType


class ResponseGenerator:
    """
    Response generator that uses Gemini API for grounded response generation.
    """

    def __init__(self):
        """
        Initialize the response generator with Gemini API configuration.
        """
        # Configure the Gemini API with the API key from settings
        genai.configure(api_key=settings.gemini_api_key)

        # Initialize the model
        self.model = genai.GenerativeModel(settings.gemini_model)

    def generate_response(
        self,
        query_text: str,
        retrieved_chunks: List[RetrievedChunk],
        query_id: str
    ) -> AgentResponse:
        """
        Generate a grounded response based on the query and retrieved chunks.

        Args:
            query_text: The original query text
            retrieved_chunks: List of relevant chunks retrieved from the database
            query_id: The ID of the original query

        Returns:
            AgentResponse object containing the generated response
        """
        try:
            # Create a context string from the retrieved chunks
            context_text = self._create_context_from_chunks(retrieved_chunks)

            # Create the prompt for the LLM
            prompt = self._create_prompt(query_text, context_text)

            # Generate the response using Gemini
            start_time = __import__('time').time()
            response = self.model.generate_content(prompt)
            generation_time = (__import__('time').time() - start_time) * 1000  # Convert to milliseconds

            # Extract the text from the response
            response_text = response.text if response.text else "I couldn't find relevant information to answer your query."

            # Create and return the AgentResponse object
            agent_response = AgentResponse.create(
                query_id=query_id,
                content=response_text,
                retrieved_chunks=retrieved_chunks,
                confidence_score=self._calculate_confidence_score(retrieved_chunks)
            )

            # Log the response generation
            logging_service.log_response_generation(
                query_id=query_id,
                response_id=agent_response.response_id,
                response_length=len(response_text),
                generation_time_ms=generation_time,
                confidence_score=agent_response.confidence_score
            )

            return agent_response

        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            logging_service.log_error(
                error=e,
                operation_context="response_generation",
                query_id=query_id
            )

            # Return a fallback response
            fallback_response = AgentResponse.create(
                query_id=query_id,
                content="I encountered an error while generating a response. Please try again later.",
                retrieved_chunks=retrieved_chunks,
                confidence_score=0.0
            )
            return fallback_response

    def _create_context_from_chunks(self, chunks: List[RetrievedChunk]) -> str:
        """
        Create a context string from the retrieved chunks.

        Args:
            chunks: List of RetrievedChunk objects

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant information found in the knowledge base."

        context_parts = ["Here is the relevant information from the knowledge base:"]
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"\n{i}. Source: {chunk.source_url}\n"
                f"   Content: {chunk.content_text}\n"
                f"   Relevance Score: {chunk.similarity_score:.2f}"
            )

        return "\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for the LLM with the query and context.

        Args:
            query: The user's query
            context: The relevant context from the knowledge base

        Returns:
            Formatted prompt string
        """
        prompt = (
            "You are an AI assistant that answers questions based strictly on the provided context.\n"
            "Only use information from the context to answer the question.\n"
            "If the context does not contain sufficient information to answer the question, "
            "please state that explicitly.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
        return prompt

    def _calculate_confidence_score(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calculate a confidence score based on the retrieved chunks.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Confidence score between 0 and 1
        """
        if not chunks:
            return 0.0

        # Calculate average similarity score of all chunks
        total_score = sum(chunk.similarity_score for chunk in chunks)
        avg_score = total_score / len(chunks)

        # Normalize to a confidence score between 0 and 1
        # Weights can be adjusted based on the number of chunks and their scores
        num_chunks_factor = min(len(chunks) / 5.0, 1.0)  # Up to 5 chunks = full weight
        confidence = (avg_score * 0.7) + (num_chunks_factor * 0.3)

        return min(confidence, 1.0)  # Ensure it doesn't exceed 1.0

    def validate_response_grounding(
        self,
        response: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> dict:
        """
        Validate that the response is grounded in the retrieved chunks.

        Args:
            response: The generated response text
            retrieved_chunks: List of chunks used to generate the response

        Returns:
            Dictionary with validation results including is_valid flag and details
        """
        # If no chunks were retrieved, the response can't be grounded in them
        if not retrieved_chunks:
            return {
                "is_valid": True,  # This is valid - no chunks to ground in
                "details": {"reason": "no_chunks_retrieved"}
            }

        # Check if the response contains key concepts from the retrieved chunks
        response_lower = response.lower()

        # Extract key terms and phrases from chunks
        key_terms = set()
        chunk_texts = []

        for chunk in retrieved_chunks:
            content_lower = chunk.content_text.lower()
            chunk_texts.append(content_lower)

            # Extract key terms (words longer than 3 characters that might be important)
            import re
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content_lower)
            key_terms.update(words)

        # Check for semantic overlap - see if key terms from chunks appear in response
        matching_terms = []
        for term in key_terms:
            if term in response_lower:
                matching_terms.append(term)

        # Check for content overlap - see if significant portions of chunk text appear in response
        content_overlap = False
        for chunk_text in chunk_texts:
            # Check if at least a portion of the chunk text appears in the response
            if len(chunk_text) > 20:  # Only check substantial chunks
                # Look for at least 10 consecutive words in common
                chunk_words = chunk_text.split()[:20]  # Take first 20 words as sample
                response_words = response_lower.split()

                # Check for phrase overlap
                for i in range(len(response_words) - 9):  # At least 10 words
                    response_phrase = ' '.join(response_words[i:i+10])
                    if len(response_phrase) > 30:  # At least 30 characters
                        for j in range(len(chunk_words) - 9):
                            chunk_phrase = ' '.join(chunk_words[j:j+10])
                            if chunk_phrase in response_phrase or response_phrase in chunk_phrase:
                                content_overlap = True
                                break
                        if content_overlap:
                            break

        # Determine if response is grounded based on multiple criteria
        has_matching_terms = len(matching_terms) > 0
        is_factually_consistent = self._check_factual_consistency(response, chunk_texts)

        is_valid = content_overlap or has_matching_terms or is_factually_consistent

        return {
            "is_valid": is_valid,
            "details": {
                "matching_terms": matching_terms,
                "content_overlap": content_overlap,
                "factual_consistency": is_factually_consistent,
                "total_chunks": len(retrieved_chunks),
                "key_terms_found": len(matching_terms)
            }
        }

    def _check_factual_consistency(self, response: str, chunk_texts: List[str]) -> bool:
        """
        Check if the response is factually consistent with the retrieved content.

        Args:
            response: The generated response
            chunk_texts: List of retrieved chunk texts

        Returns:
            True if the response appears factually consistent, False otherwise
        """
        # This is a basic check - in a more sophisticated implementation,
        # we might use more advanced NLP techniques
        response_lower = response.lower()

        # Look for consistency indicators
        for chunk_text in chunk_texts:
            # Check if response acknowledges limitations of the provided information
            if "i don't know" in response_lower or "not mentioned" in response_lower:
                # If the response admits lack of information, it's consistent
                return True

            # Check if response makes claims that contradict the source
            # For now, we'll keep this simple
            if len(chunk_text) > 50:  # Only consider substantial chunks
                # Look for agreement between response and source
                chunk_words = set(chunk_text.split()[:50])  # First 50 words
                response_words = set(response_lower.split())

                # If there's some overlap in content words, consider it consistent
                common_words = chunk_words.intersection(response_words)
                if len(common_words) > 2:  # At least 3 common content words
                    return True

        return False


# Global response generator instance
response_generator = ResponseGenerator()