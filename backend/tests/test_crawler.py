"""
Tests for the Website Crawler Module

This module contains unit tests for the website crawling functionality
of the RAG URL ingestion pipeline.
"""

import pytest
from unittest.mock import Mock, patch
from src.crawler.website_crawler import WebsiteCrawler
from src.config.settings import Settings


class TestWebsiteCrawler:
    """Test cases for the WebsiteCrawler class."""

    @pytest.fixture
    def settings(self):
        """Provide test settings."""
        # Mock environment variables
        with patch.dict('os.environ', {
            'COHERE_API_KEY': 'test-key',
            'QDRANT_URL': 'https://test.qdrant.com'
        }):
            return Settings()

    @pytest.fixture
    def crawler(self, settings):
        """Provide a crawler instance."""
        return WebsiteCrawler(settings)

    def test_valid_url_check(self, crawler):
        """Test URL validation."""
        assert crawler._is_valid_url("https://example.com")
        assert crawler._is_valid_url("http://example.com")
        assert not crawler._is_valid_url("invalid-url")
        assert not crawler._is_valid_url("")

    def test_crawl_single_url_success(self, crawler):
        """Test crawling a single URL successfully."""
        # Mock the requests.get method to return a successful response
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body><p>Test content</p></body></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = crawler.crawl_single_url("https://example.com")

            assert result['url'] == "https://example.com"
            assert "Test content" in result['content']

    def test_crawl_single_url_failure(self, crawler):
        """Test crawling a single URL with failure."""
        # Mock the requests.get method to raise an exception
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")

            result = crawler.crawl_single_url("https://example.com")

            assert result == {}

    def test_crawl_urls_multiple(self, crawler):
        """Test crawling multiple URLs."""
        # Mock the requests.get method to return successful responses
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html><body><p>Test content</p></body></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            urls = ["https://example1.com", "https://example2.com"]
            results = crawler.crawl_urls(urls)

            assert len(results) == 2
            for result in results:
                assert "Test content" in result['content']