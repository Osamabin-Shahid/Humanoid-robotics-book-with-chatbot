"""
Query Generator

This module handles converting natural language queries to embeddings
for the RAG retrieval and validation system.
"""
import cohere
import logging
from typing import List
from src.config.settings import Settings
from src.embedding.models import EmbeddingVector
from src.utils.retry_utils import retry_with_exponential_backoff


class QueryEmbeddingGenerator:
    """
    Generator for creating embeddings from user queries using Cohere API.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the query embedding generator with settings.
        """
        self.settings = settings
        self.client = cohere.Client(settings.cohere_api_key)

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        allowed_exceptions=(Exception,)  # Using generic Exception to avoid import issues
    )
    def generate_query_embedding(self, query_text: str, model: str = None) -> EmbeddingVector:
        """
        Generate an embedding for a single query text.

        Args:
            query_text: The natural language query text
            model: The model to use for embedding (optional)

        Returns:
            EmbeddingVector: The generated embedding vector
        """
        if not model:
            model = self.settings.cohere_model

        try:
            response = self.client.embed(
                texts=[query_text],
                model=model
            )

            embedding_data = response.embeddings[0]
            dimension = len(embedding_data)

            # For query embeddings, we don't need a persistent ID like we do for stored chunks
            # We can generate a temporary ID for this session
            import uuid
            vector_id = f"query_{str(uuid.uuid4())[:8]}"

            return EmbeddingVector(
                vector_id=vector_id,
                vector_data=embedding_data,
                model_name=model,
                model_version="",  # Cohere doesn't provide model version in response
                dimension=dimension
            )
        except cohere.errors.RateLimitError as e:
            logging.error(f"Rate limit exceeded when generating query embedding: {str(e)}")
            raise e
        except cohere.errors.CohereAPIError as e:
            logging.error(f"Cohere API error when generating query embedding: {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Unexpected error generating query embedding: {str(e)}")
            raise Exception(f"Error generating query embedding: {str(e)}")

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        allowed_exceptions=(Exception,)  # Using generic Exception to avoid import issues
    )
    def generate_query_embeddings(self, query_texts: List[str], model: str = None) -> List[EmbeddingVector]:
        """
        Generate embeddings for a list of query texts.

        Args:
            query_texts: List of natural language query texts
            model: The model to use for embedding (optional)

        Returns:
            List[EmbeddingVector]: The generated embedding vectors
        """
        if not model:
            model = self.settings.cohere_model

        try:
            response = self.client.embed(
                texts=query_texts,
                model=model
            )

            embeddings = []
            for i, embedding_data in enumerate(response.embeddings):
                dimension = len(embedding_data)

                import uuid
                vector_id = f"query_{str(uuid.uuid4())[:8]}_{i}"

                embedding = EmbeddingVector(
                    vector_id=vector_id,
                    vector_data=embedding_data,
                    model_name=model,
                    model_version="",  # Cohere doesn't provide model version in response
                    dimension=dimension
                )
                embeddings.append(embedding)

            return embeddings
        except cohere.errors.RateLimitError as e:
            logging.error(f"Rate limit exceeded when generating query embeddings: {str(e)}")
            raise e
        except cohere.errors.CohereAPIError as e:
            logging.error(f"Cohere API error when generating query embeddings: {str(e)}")
            raise e
        except Exception as e:
            logging.error(f"Unexpected error generating query embeddings: {str(e)}")
            raise Exception(f"Error generating query embeddings: {str(e)}")

    def get_query_embedding(self, query_text: str) -> List[float]:
        """
        Get just the embedding vector data (list of floats) for a query.

        Args:
            query_text: The natural language query text

        Returns:
            List[float]: The embedding vector as a list of floats
        """
        embedding_vector = self.generate_query_embedding(query_text)
        return embedding_vector.vector_data

    def validate_query_text(self, query_text: str) -> bool:
        """
        Validate that the query text is suitable for embedding.

        Args:
            query_text: The query text to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty or just whitespace")

        if len(query_text.strip()) > 5000:  # Cohere has limits
            raise ValueError("Query text is too long (max 5000 characters)")

        return True