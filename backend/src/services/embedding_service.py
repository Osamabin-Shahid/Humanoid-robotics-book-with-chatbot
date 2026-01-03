"""
Embedding Service

This module manages the embedding generation process
for the RAG URL ingestion pipeline.
"""

from typing import List
from src.config.settings import Settings
from src.embedding.generator import EmbeddingGenerator
from src.models.chunk_model import TextChunk
from src.embedding.models import EmbeddingVector
from src.utils.helpers import Helpers


class EmbeddingService:
    """Service to manage the embedding generation process."""

    def __init__(self, settings: Settings):
        """Initialize the embedding service with settings."""
        self.settings = settings
        self.generator = EmbeddingGenerator(settings)

    def generate_embedding_for_chunk(self, chunk: TextChunk, model: str = None) -> EmbeddingVector:
        """Generate an embedding for a single text chunk."""
        try:
            embedding = self.generator.generate_embedding(chunk.content, model)
            embedding.source_chunk_id = chunk.chunk_id
            embedding.validate()
            return embedding
        except Exception as e:
            raise Exception(f"Error generating embedding for chunk {chunk.chunk_id}: {str(e)}")

    def generate_embeddings_for_chunks(self, chunks: List[TextChunk], model: str = None) -> List[EmbeddingVector]:
        """Generate embeddings for a list of text chunks."""
        if not chunks:
            return []

        try:
            # Process in batches to avoid hitting API limits
            batch_size = 96  # Cohere's recommended batch size
            all_embeddings = []

            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch_texts = [chunk.content for chunk in batch]

                # Retry with backoff for API rate limits
                batch_embeddings = self._generate_embeddings_with_retry(batch_texts, model)

                # Link embeddings back to chunks
                for j, embedding in enumerate(batch_embeddings):
                    embedding.source_chunk_id = batch[j].chunk_id
                    embedding.validate()
                    all_embeddings.append(embedding)

            return all_embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings for chunks: {str(e)}")

    def _generate_embeddings_with_retry(self, texts: List[str], model: str = None) -> List[EmbeddingVector]:
        """Generate embeddings with retry logic for rate limits."""
        max_retries = self.settings.max_retries
        base_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                return self.generator.generate_embeddings(texts, model)
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e

                # Check if it's a rate limit error and wait before retrying
                import time
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"Rate limit or error encountered, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)

        return []

    def validate_embedding(self, embedding: EmbeddingVector) -> bool:
        """Validate an embedding vector."""
        return embedding.validate()

    def get_model_info(self, model: str = None) -> dict:
        """Get information about the embedding model."""
        return self.generator.get_model_info(model)

    def calculate_token_count(self, text: str) -> int:
        """Calculate approximate token count for a text."""
        return Helpers.calculate_token_count(text)