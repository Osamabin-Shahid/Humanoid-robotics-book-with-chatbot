"""
Tests for Incremental Update Functionality

This module contains unit tests for the incremental update functionality
of the RAG URL ingestion pipeline.
"""

import pytest
from unittest.mock import patch, Mock
from src.services.crawling_service import CrawlingService
from src.config.settings import Settings
from src.models.chunk_model import TextChunk


class TestIncrementalUpdates:
    """Test cases for incremental update functionality."""

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
    def mock_crawler(self):
        """Provide a mock website crawler."""
        with patch('src.crawler.website_crawler.WebsiteCrawler') as mock_crawler:
            mock_instance = Mock()
            mock_instance.crawl_single_url.return_value = {
                'url': 'https://example.com',
                'content': 'Updated content',
                'title': 'Test Page'
            }
            mock_crawler.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_chunker(self):
        """Provide a mock text chunker."""
        with patch('src.chunking.text_chunker.TextChunker') as mock_chunker:
            mock_instance = Mock()
            mock_instance.chunk_text.return_value = [
                {
                    'chunk_id': 'chunk_test_0001_abc123',
                    'content': 'Updated content',
                    'source_url': 'https://example.com',
                    'section': 'Test Page',
                    'sequence_number': 0,
                    'token_count': 2,
                    'hash': 'def456'
                }
            ]
            mock_chunker.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def crawling_service(self, settings, mock_crawler, mock_chunker):
        """Provide a crawling service instance."""
        service = CrawlingService(settings)
        service.crawler = mock_crawler
        service.chunker = mock_chunker
        return service

    def test_content_change_detection(self, crawling_service):
        """Test detection of content changes."""
        # Create existing chunks
        existing_chunks = [
            TextChunk(
                chunk_id="chunk1",
                content="Original content",
                source_url="https://example.com"
            )
        ]

        # Create current chunks
        current_chunks = [
            TextChunk(
                chunk_id="chunk1",
                content="Updated content",
                source_url="https://example.com"
            )
        ]

        changes = crawling_service._detect_content_changes(current_chunks, existing_chunks)

        assert len(changes['updated']) == 1
        assert len(changes['unchanged']) == 0
        assert len(changes['new']) == 0

    def test_unchanged_content_detection(self, crawling_service):
        """Test detection of unchanged content."""
        # Create existing chunks
        existing_chunks = [
            TextChunk(
                chunk_id="chunk1",
                content="Same content",
                source_url="https://example.com"
            )
        ]

        # Create current chunks with same content
        current_chunks = [
            TextChunk(
                chunk_id="chunk1",
                content="Same content",
                source_url="https://example.com"
            )
        ]

        changes = crawling_service._detect_content_changes(current_chunks, existing_chunks)

        assert len(changes['updated']) == 0
        assert len(changes['unchanged']) == 1
        assert len(changes['new']) == 0

    def test_new_content_detection(self, crawling_service):
        """Test detection of new content."""
        # No existing chunks
        existing_chunks = []

        # Create current chunks
        current_chunks = [
            TextChunk(
                chunk_id="chunk1",
                content="New content",
                source_url="https://example.com"
            )
        ]

        changes = crawling_service._detect_content_changes(current_chunks, existing_chunks)

        assert len(changes['updated']) == 0
        assert len(changes['unchanged']) == 0
        assert len(changes['new']) == 1