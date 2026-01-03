"""
Tests for the Storage Module

This module contains unit tests for the storage functionality
of the RAG URL ingestion pipeline.
"""

import pytest
from unittest.mock import patch, Mock
from src.storage.qdrant_client import QdrantCloudClient
from src.services.storage_service import StorageService
from src.config.settings import Settings
from src.embedding.models import EmbeddingVector
from src.models.chunk_model import TextChunk


class TestQdrantCloudClient:
    """Test cases for the QdrantCloudClient class."""

    @pytest.fixture
    def settings(self):
        """Provide test settings."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'COHERE_API_KEY': 'test-key',
            'QDRANT_URL': 'https://test.qdrant.com',
            'QDRANT_API_KEY': 'test-api-key'
        }):
            settings = Settings()
            settings.qdrant_collection_name = "test_collection"
            return settings

    @pytest.fixture
    def mock_qdrant_client(self):
        """Provide a mock Qdrant client."""
        with patch('qdrant_client.QdrantClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def qdrant_client(self, settings, mock_qdrant_client):
        """Provide a Qdrant client instance."""
        client = QdrantCloudClient(settings)
        client.client = mock_qdrant_client
        return client

    def test_create_collection(self, qdrant_client):
        """Test creating a collection."""
        qdrant_client.client.get_collections.return_value = Mock(collections=[])
        qdrant_client.client.create_collection.return_value = True

        result = qdrant_client.create_collection(vector_size=768)
        assert result is True

    def test_store_embedding(self, qdrant_client):
        """Test storing a single embedding."""
        embedding = EmbeddingVector(
            vector_id="test_id",
            vector_data=[0.1, 0.2, 0.3],
            model_name="test_model",
            model_version="",
            dimension=3
        )
        from src.storage.models import Metadata
        metadata = Metadata(
            chunk_id="chunk1",
            source_url="https://example.com"
        )

        qdrant_client.client.upsert.return_value = True

        result = qdrant_client.store_embedding(embedding, metadata)
        assert result is True
        qdrant_client.client.upsert.assert_called_once()

    def test_search_similar(self, qdrant_client):
        """Test searching for similar vectors."""
        mock_result = [Mock()]
        mock_result[0].id = "result1"
        mock_result[0].score = 0.9
        mock_result[0].payload = {"chunk_id": "chunk1"}
        mock_result[0].vector = [0.1, 0.2, 0.3]

        qdrant_client.client.search.return_value = mock_result

        results = qdrant_client.search_similar([0.1, 0.2, 0.3])
        assert len(results) == 1
        assert results[0]['id'] == "result1"


class TestStorageService:
    """Test cases for the StorageService class."""

    @pytest.fixture
    def settings(self):
        """Provide test settings."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'COHERE_API_KEY': 'test-key',
            'QDRANT_URL': 'https://test.qdrant.com',
            'QDRANT_API_KEY': 'test-api-key'
        }):
            settings = Settings()
            settings.qdrant_collection_name = "test_collection"
            return settings

    @pytest.fixture
    def mock_qdrant_client(self):
        """Provide a mock Qdrant client."""
        with patch('src.storage.qdrant_client.QdrantCloudClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def service(self, settings, mock_qdrant_client):
        """Provide a storage service instance."""
        service = StorageService(settings)
        service.client = mock_qdrant_client
        return service

    def test_store_embedding_with_metadata(self, service):
        """Test storing an embedding with metadata."""
        embedding = EmbeddingVector(
            vector_id="test_id",
            vector_data=[0.1, 0.2, 0.3],
            model_name="test_model",
            model_version="",
            dimension=3
        )
        chunk = TextChunk(
            chunk_id="chunk1",
            content="Test content",
            source_url="https://example.com"
        )

        service.client.store_embedding.return_value = True

        result = service.store_embedding_with_metadata(embedding, chunk)
        assert result is True

    def test_store_embeddings_with_metadata(self, service):
        """Test storing multiple embeddings with metadata."""
        embeddings = [
            EmbeddingVector(
                vector_id="test_id1",
                vector_data=[0.1, 0.2, 0.3],
                model_name="test_model",
                model_version="",
                dimension=3
            )
        ]
        chunks = [
            TextChunk(
                chunk_id="chunk1",
                content="Test content",
                source_url="https://example.com"
            )
        ]

        service.client.store_embeddings.return_value = 1

        result = service.store_embeddings_with_metadata(embeddings, chunks)
        assert result.success is True
        assert result.stored_count == 1