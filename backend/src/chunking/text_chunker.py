"""
Text Chunker Module

This module handles splitting text into configurable chunks with overlap
for the RAG URL ingestion pipeline.
"""

import hashlib
from typing import List, Dict, Any
from src.config.settings import Settings


class TextChunker:
    """Chunker for splitting text into configurable chunks with overlap."""

    def __init__(self, settings: Settings):
        """Initialize the chunker with settings."""
        self.settings = settings

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization by splitting on whitespace."""
        return text.split()

    def _detokenize(self, tokens: List[str]) -> str:
        """Join tokens back into text."""
        return ' '.join(tokens)

    def _calculate_chunk_size(self, tokens: List[str]) -> int:
        """Calculate the effective chunk size based on settings."""
        return int(self.settings.chunk_size * (1 - self.settings.overlap_percentage))

    def chunk_text(self, text: str, source_url: str, section: str = "") -> List[Dict[str, Any]]:
        """Chunk text with configurable size and overlap."""
        if not text:
            return []

        tokens = self._tokenize(text)
        chunk_size = self.settings.chunk_size
        overlap_size = int(chunk_size * self.settings.overlap_percentage)
        step_size = chunk_size - overlap_size

        if len(tokens) <= chunk_size:
            # If text is smaller than chunk size, return as single chunk
            content = self._detokenize(tokens)
            chunk_id = self._generate_chunk_id(content, source_url, 0)
            return [{
                'chunk_id': chunk_id,
                'content': content,
                'source_url': source_url,
                'section': section,
                'sequence_number': 0,
                'token_count': len(tokens),
                'hash': self._generate_content_hash(content)
            }]

        chunks = []
        start_idx = 0
        sequence_number = 0

        while start_idx < len(tokens):
            end_idx = min(start_idx + chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            content = self._detokenize(chunk_tokens)

            chunk_id = self._generate_chunk_id(content, source_url, sequence_number)
            chunk_data = {
                'chunk_id': chunk_id,
                'content': content,
                'source_url': source_url,
                'section': section,
                'sequence_number': sequence_number,
                'token_count': len(chunk_tokens),
                'hash': self._generate_content_hash(content)
            }

            chunks.append(chunk_data)

            # Move to next chunk position
            start_idx += step_size
            sequence_number += 1

            # Break if we've reached the end
            if start_idx >= len(tokens):
                break

        return chunks

    def _generate_chunk_id(self, content: str, source_url: str, sequence_number: int) -> str:
        """Generate a unique chunk ID based on content, URL, and sequence."""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        url_hash = hashlib.md5(source_url.encode('utf-8')).hexdigest()[:8]
        return f"chunk_{url_hash}_{sequence_number:04d}_{content_hash}"

    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()