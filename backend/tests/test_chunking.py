"""
Tests for the Text Chunker Module

This module contains unit tests for the text chunking functionality
of the RAG URL ingestion pipeline.
"""

import pytest
from unittest.mock import patch
from src.chunking.text_chunker import TextChunker
from src.config.settings import Settings


class TestTextChunker:
    """Test cases for the TextChunker class."""

    @pytest.fixture
    def settings(self):
        """Provide test settings."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'COHERE_API_KEY': 'test-key',
            'QDRANT_URL': 'https://test.qdrant.com'
        }):
            settings = Settings()
            settings.chunk_size = 10
            settings.overlap_percentage = 0.2
            return settings

    @pytest.fixture
    def chunker(self, settings):
        """Provide a chunker instance."""
        return TextChunker(settings)

    def test_chunk_empty_text(self, chunker):
        """Test chunking empty text."""
        result = chunker.chunk_text("", "https://example.com")
        assert len(result) == 0

    def test_chunk_small_text(self, chunker):
        """Test chunking text smaller than chunk size."""
        text = "This is a short text"
        result = chunker.chunk_text(text, "https://example.com")

        assert len(result) == 1
        assert result[0]['content'] == text
        assert result[0]['source_url'] == "https://example.com"

    def test_chunk_text_with_overlap(self, settings):
        """Test chunking text with overlap."""
        settings.chunk_size = 5
        settings.overlap_percentage = 0.2  # 1 token overlap
        chunker = TextChunker(settings)

        text = "This is a longer text for testing chunking with overlap"
        result = chunker.chunk_text(text, "https://example.com")

        assert len(result) > 1  # Should be split into multiple chunks
        # Check that chunks have expected properties
        for chunk in result:
            assert 'chunk_id' in chunk
            assert 'content' in chunk
            assert 'source_url' in chunk
            assert len(chunk['content']) > 0

    def test_chunk_text_without_overlap(self, settings):
        """Test chunking text without overlap."""
        settings.chunk_size = 4
        settings.overlap_percentage = 0.0  # No overlap
        chunker = TextChunker(settings)

        text = "This is a test text for chunking"
        result = chunker.chunk_text(text, "https://example.com", section="Test Section")

        assert len(result) > 1
        # Verify section is preserved
        for chunk in result:
            assert chunk['section'] == "Test Section"