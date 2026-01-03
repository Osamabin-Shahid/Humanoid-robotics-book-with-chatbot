"""
Tests for the API Endpoints

This module contains unit tests for the API endpoints
of the RAG URL ingestion pipeline.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.config.settings import Settings
from main_api import create_app


@pytest.fixture
def client():
    """Provide a test client for the API."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Test cases for the health endpoint."""

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "unhealthy"]

    def test_readiness_check(self, client):
        """Test the readiness check endpoint."""
        response = client.get("/api/v1/ready")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] in ["ready", "unready"]


class TestCrawlEndpoint:
    """Test cases for the crawl endpoint."""

    def test_crawl_endpoint_valid_request(self, client):
        """Test the crawl endpoint with a valid request."""
        # Mock the crawling service to avoid actual crawling
        with patch('src.services.crawling_service.CrawlingService') as mock_crawling_service:
            mock_service_instance = Mock()
            mock_service_instance.process_urls.return_value = Mock(
                crawl_id="test_crawl_123",
                status="success",
                pages_processed=1,
                total_chunks=2,
                error_count=0,
                start_time=Mock(isoformat=lambda: "2023-01-01T00:00:00"),
                end_time=Mock(isoformat=lambda: "2023-01-01T00:01:00"),
                processed_urls=["https://example.com"],
                error_details=[]
            )
            mock_crawling_service.return_value = mock_service_instance

            request_data = {
                "urls": ["https://example.com"],
                "configuration": {
                    "chunk_size": 512,
                    "overlap_percentage": 0.2
                }
            }

            response = client.post("/api/v1/crawl", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert data["crawl_id"] == "test_crawl_123"
            assert data["status"] == "success"
            assert data["pages_processed"] == 1


class TestEmbedEndpoint:
    """Test cases for the embed endpoint."""

    def test_embed_endpoint_valid_request(self, client):
        """Test the embed endpoint with a valid request."""
        # Mock the embedding service to avoid actual API calls
        with patch('src.services.embedding_service.EmbeddingService') as mock_embedding_service:
            mock_service_instance = Mock()
            mock_service_instance.generate_embeddings_for_chunks.return_value = [
                Mock(
                    source_chunk_id="chunk1",
                    vector_data=[0.1, 0.2, 0.3],
                    model_name="test-model",
                    dimension=3
                )
            ]
            mock_embedding_service.return_value = mock_service_instance

            request_data = {
                "chunks": [
                    {
                        "chunk_id": "chunk1",
                        "content": "This is a test sentence.",
                        "source_url": "https://example.com"
                    }
                ],
                "model": "test-model"
            }

            response = client.post("/api/v1/embed", json=request_data)
            assert response.status_code == 200

            data = response.json()
            assert len(data["embeddings"]) == 1
            assert data["total_processed"] == 1
            assert data["model"] == "test-model"