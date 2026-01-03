"""
Website Crawler Module

This module handles crawling websites to extract text content
for the RAG URL ingestion pipeline.
"""

import time
import requests
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from src.config.settings import Settings


class WebsiteCrawler:
    """Crawler for extracting content from websites."""

    def __init__(self, settings: Settings):
        """Initialize the crawler with settings."""
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-URL-Pipeline/1.0'
        })

        # Rate limiting tracking
        self.last_request_time = 0
        self.rate_limit_delay = self.settings.rate_limit_period / self.settings.rate_limit_requests

    def _respect_rate_limit(self):
        """Ensure we respect the rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _is_valid_url(self, url: str) -> bool:
        """Check if the URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _get_page_content(self, url: str) -> Optional[str]:
        """Fetch and return the content of a single page."""
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        self._respect_rate_limit()

        try:
            response = self.session.get(
                url,
                timeout=self.settings.timeout_seconds,
                headers={'User-Agent': 'RAG-URL-Pipeline/1.0'}
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def crawl_single_url(self, url: str) -> Dict[str, str]:
        """Crawl a single URL and return its content."""
        content = self._get_page_content(url)
        if content is None:
            return {}

        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text (remove extra whitespace)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return {
                'url': url,
                'content': text,
                'title': soup.title.string if soup.title else ''
            }
        except Exception as e:
            print(f"Error parsing content from {url}: {str(e)}")
            return {}

    def crawl_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """Crawl multiple URLs and return their content."""
        results = []
        for url in urls:
            print(f"Crawling: {url}")
            content_data = self.crawl_single_url(url)
            if content_data:
                results.append(content_data)

        return results