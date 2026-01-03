"""
Text Extractor Module

This module handles extracting clean text from HTML content
for the RAG URL ingestion pipeline.
"""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup


class TextExtractor:
    """Extractor for cleaning and processing text content."""

    def __init__(self):
        """Initialize the text extractor."""
        pass

    def extract_text(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        if not html_content:
            return ""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text (remove extra whitespace)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return ""

    def extract_content_with_structure(self, html_content: str) -> List[Tuple[str, str]]:
        """Extract content while preserving some structure (headers, paragraphs)."""
        if not html_content:
            return []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            content_parts = []

            # Process different elements
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section']):
                text = element.get_text().strip()
                if text:
                    tag = element.name
                    content_parts.append((tag, text))

            return content_parts
        except Exception as e:
            print(f"Error extracting structured content: {str(e)}")
            return []

    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text