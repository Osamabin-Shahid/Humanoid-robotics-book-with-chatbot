"""
Embedding Generator

This module handles generating embeddings using Cohere
for the RAG URL ingestion pipeline.
"""

import cohere
from typing import List, Dict, Any
from src.config.settings import Settings
from src.models.chunk_model import TextChunk
from src.embedding.models import EmbeddingVector
from src.utils.helpers import Helpers


class EmbeddingGenerator:
    """Generator for creating embeddings using Cohere API."""

    def __init__(self, settings: Settings):
        """Initialize the embedding generator with settings."""
        self.settings = settings
        self.client = cohere.Client(settings.cohere_api_key)

    def generate_embedding(self, text: str, model: str = None) -> EmbeddingVector:
        """Generate a single embedding for the given text."""
        if not model:
            model = self.settings.cohere_model if hasattr(self.settings, 'cohere_model') else "embed-multilingual-v2.0"

        try:
            response = self.client.embed(
                texts=[text],
                model=model
            )

            embedding_data = response.embeddings[0]
            dimension = len(embedding_data)

            import uuid
            vector_id = str(uuid.uuid4())

            return EmbeddingVector(
                vector_id=vector_id,
                vector_data=embedding_data,
                model_name=model,
                model_version="",  # Cohere doesn't provide model version in response
                dimension=dimension
            )
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    def generate_embeddings(self, texts: List[str], model: str = None) -> List[EmbeddingVector]:
        """Generate embeddings for a list of texts."""
        if not model:
            model = self.settings.cohere_model if hasattr(self.settings, 'cohere_model') else "embed-multilingual-v2.0"

        try:
            response = self.client.embed(
                texts=texts,
                model=model
            )

            embeddings = []
            for i, embedding_data in enumerate(response.embeddings):
                dimension = len(embedding_data)
                import uuid
                vector_id = str(uuid.uuid4())

                embedding = EmbeddingVector(
                    vector_id=vector_id,
                    vector_data=embedding_data,
                    model_name=model,
                    model_version="",  # Cohere doesn't provide model version in response
                    dimension=dimension
                )
                embeddings.append(embedding)

            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")

    def generate_embeddings_from_chunks(self, chunks: List[TextChunk], model: str = None) -> List[EmbeddingVector]:
        """Generate embeddings for a list of text chunks."""
        if not model:
            model = self.settings.cohere_model if hasattr(self.settings, 'cohere_model') else "embed-multilingual-v2.0"

        # Extract text content from chunks
        texts = [chunk.content for chunk in chunks]

        try:
            response = self.client.embed(
                texts=texts,
                model=model
            )

            embeddings = []
            for i, embedding_data in enumerate(response.embeddings):
                dimension = len(embedding_data)
                import uuid
                vector_id = str(uuid.uuid4())

                embedding = EmbeddingVector(
                    vector_id=vector_id,
                    vector_data=embedding_data,
                    model_name=model,
                    model_version="",  # Cohere doesn't provide model version in response
                    dimension=dimension,
                    source_chunk_id=chunks[i].chunk_id
                )
                embeddings.append(embedding)

            return embeddings
        except Exception as e:
            raise Exception(f"Error generating embeddings from chunks: {str(e)}")

    def get_model_info(self, model: str = None) -> Dict[str, Any]:
        """Get information about the embedding model."""
        if not model:
            model = self.settings.cohere_model if hasattr(self.settings, 'cohere_model') else "embed-multilingual-v2.0"

        # Note: Cohere API doesn't have a direct method to get model info
        # We'll return basic info based on common Cohere models
        model_info = {
            'model_name': model,
            'dimensions': self._get_expected_dimensions(model)
        }
        return model_info

    def _get_expected_dimensions(self, model: str) -> int:
        """Get expected dimensions for a given model."""
        # Common Cohere embedding model dimensions
        model_dims = {
            "embed-english-v2.0": 4096,
            "embed-english-light-v2.0": 1024,
            "embed-multilingual-v2.0": 768,
            "embed-multilingual-light-v2.0": 384
        }
        return model_dims.get(model, 768)  # Default to multilingual model dimension