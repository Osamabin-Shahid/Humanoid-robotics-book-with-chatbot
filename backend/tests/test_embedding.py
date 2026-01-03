"""
Tests for the Embedding Module

This module contains unit tests for the embedding functionality
of the RAG URL ingestion pipeline.
"""

import pytest
from unittest.mock import patch, Mock
from src.embedding.generator import EmbeddingGenerator
from src.services.embedding_service import EmbeddingService
from src.config.settings import Settings
from src.models.chunk_model import TextChunk


class TestEmbeddingGenerator:
    """Test cases for the EmbeddingGenerator class."""

    @pytest.fixture
    def settings(self):
        """Provide test settings."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'COHERE_API_KEY': 'test-key',
            'QDRANT_URL': 'https://test.qdrant.com'
        }):
            settings = Settings()
            return settings

    @pytest.fixture
    def mock_cohere_client(self):
        """Provide a mock Cohere client."""
        with patch('cohere.Client') as mock_client:
            mock_instance = Mock()
            mock_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def generator(self, settings, mock_cohere_client):
        """Provide an embedding generator instance."""
        generator = EmbeddingGenerator(settings)
        generator.client = mock_cohere_client
        return generator

    def test_generate_embedding(self, generator):
        """Test generating a single embedding."""
        text = "This is a test text"
        embedding = generator.generate_embedding(text)

        assert embedding.vector_id.startswith("emb_")
        assert embedding.vector_data == [0.1, 0.2, 0.3]
        assert embedding.model_name == "embed-multilingual-v2.0"

    def test_generate_embeddings(self, generator):
        """Test generating multiple embeddings."""
        texts = ["Text 1", "Text 2"]
        embeddings = generator.generate_embeddings(texts)

        assert len(embeddings) == 2
        for embedding in embeddings:
            assert embedding.vector_id.startswith("emb_")
            assert embedding.vector_data == [0.1, 0.2, 0.3]

    def test_generate_embeddings_from_chunks(self, generator):
        """Test generating embeddings from text chunks."""
        chunks = [
            TextChunk("chunk1", "Text 1", "https://example.com/1"),
            TextChunk("chunk2", "Text 2", "https://example.com/2")
        ]
        embeddings = generator.generate_embeddings_from_chunks(chunks)

        assert len(embeddings) == 2
        for i, embedding in enumerate(embeddings):
            assert embedding.source_chunk_id == chunks[i].chunk_id


class TestEmbeddingService:
    """Test cases for the EmbeddingService class."""

    @pytest.fixture
    def settings(self):
        """Provide test settings."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'COHERE_API_KEY': 'test-key',
            'QDRANT_URL': 'https://test.qdrant.com'
        }):
            settings = Settings()
            return settings

    @pytest.fixture
    def mock_generator(self):
        """Provide a mock embedding generator."""
        with patch('src.embedding.generator.EmbeddingGenerator') as mock_gen:
            mock_instance = Mock()
            mock_instance.generate_embedding.return_value = Mock(
                vector_id="emb_test",
                vector_data=[0.1, 0.2, 0.3],
                model_name="test-model",
                model_version="",
                dimension=3,
                source_chunk_id="chunk1"
            )
            mock_instance.generate_embeddings.return_value = [
                Mock(
                    vector_id="emb_test1",
                    vector_data=[0.1, 0.2, 0.3],
                    model_name="test-model",
                    model_version="",
                    dimension=3,
                    source_chunk_id="chunk1"
                ),
                Mock(
                    vector_id="emb_test2",
                    vector_data=[0.4, 0.5, 0.6],
                    model_name="test-model",
                    model_version="",
                    dimension=3,
                    source_chunk_id="chunk2"
                )
            ]
            mock_gen.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def service(self, settings, mock_generator):
        """Provide an embedding service instance."""
        service = EmbeddingService(settings)
        service.generator = mock_generator
        return service

    def test_generate_embedding_for_chunk(self, service):
        """Test generating embedding for a single chunk."""
        chunk = TextChunk("chunk1", "Test content", "https://example.com")
        embedding = service.generate_embedding_for_chunk(chunk)

        assert embedding.source_chunk_id == "chunk1"
        assert embedding.vector_id == "emb_test"

    def test_generate_embeddings_for_chunks(self, service):
        """Test generating embeddings for multiple chunks."""
        chunks = [
            TextChunk("chunk1", "Text 1", "https://example.com/1"),
            TextChunk("chunk2", "Text 2", "https://example.com/2")
        ]
        embeddings = service.generate_embeddings_for_chunks(chunks)

        assert len(embeddings) == 2
        for i, embedding in enumerate(embeddings):
            assert embedding.source_chunk_id == chunks[i].chunk_id