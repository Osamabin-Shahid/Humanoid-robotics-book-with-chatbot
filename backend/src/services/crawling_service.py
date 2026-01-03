"""
Crawling Service

This module orchestrates the crawling process for the RAG URL ingestion pipeline.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any
from src.config.settings import Settings
from src.crawler.website_crawler import WebsiteCrawler
from src.crawler.text_extractor import TextExtractor
from src.chunking.text_chunker import TextChunker
from src.models.crawl_result_model import CrawlResult
from src.models.chunk_model import TextChunk
from src.models.pipeline_config_model import PipelineConfig


class CrawlingService:
    """Service to orchestrate the crawling, extraction, and chunking process."""

    def __init__(self, settings: Settings):
        """Initialize the crawling service with settings."""
        self.settings = settings
        self.crawler = WebsiteCrawler(settings)
        self.extractor = TextExtractor()
        self.chunker = TextChunker(settings)
        self.config = PipelineConfig.from_settings(settings)

    def _detect_content_changes(self, current_chunks: List[TextChunk], existing_chunks: List[TextChunk] = None) -> Dict[str, List[TextChunk]]:
        """Detect which chunks have changed, which are new, and which are unchanged."""
        if existing_chunks is None:
            existing_chunks = []

        # Create a map of existing chunks by their hash
        existing_by_hash = {chunk.hash: chunk for chunk in existing_chunks}

        unchanged_chunks = []
        updated_chunks = []
        new_chunks = []

        for chunk in current_chunks:
            if chunk.hash in existing_by_hash:
                # Content exists but may have changed
                existing_chunk = existing_by_hash[chunk.hash]
                if chunk.content == existing_chunk.content:
                    unchanged_chunks.append(chunk)
                else:
                    updated_chunks.append(chunk)
            else:
                # New content
                new_chunks.append(chunk)

        return {
            'unchanged': unchanged_chunks,
            'updated': updated_chunks,
            'new': new_chunks
        }

    def process_urls(self, urls: List[str], chunk_size: int = None, overlap_percentage: float = None, incremental: bool = False) -> CrawlResult:
        """Process a list of URLs through the full pipeline."""
        crawl_result, _ = self._process_urls_internal(urls, chunk_size, overlap_percentage, incremental)
        return crawl_result

    def process_urls_with_chunks(self, urls: List[str], chunk_size: int = None, overlap_percentage: float = None, incremental: bool = False) -> tuple[CrawlResult, List[TextChunk]]:
        """Process a list of URLs and return both crawl result and the chunks."""
        return self._process_urls_internal(urls, chunk_size, overlap_percentage, incremental)

    def _process_urls_internal(self, urls: List[str], chunk_size: int = None, overlap_percentage: float = None, incremental: bool = False) -> tuple[CrawlResult, List[TextChunk]]:
        """Internal method to process URLs and return both crawl result and chunks."""
        if chunk_size is not None:
            self.settings.chunk_size = chunk_size
        if overlap_percentage is not None:
            self.settings.overlap_percentage = overlap_percentage

        crawl_id = f"crawl_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()

        all_chunks = []
        processed_urls = []
        error_count = 0
        error_details = []

        for url in urls:
            try:
                print(f"Processing URL: {url}")
                # Crawl the URL
                crawled_data = self.crawler.crawl_single_url(url)

                if not crawled_data:
                    error_count += 1
                    error_details.append({
                        'url': url,
                        'error': 'Failed to crawl URL'
                    })
                    continue

                # Extract text content
                content = crawled_data.get('content', '')
                if not content:
                    error_count += 1
                    error_details.append({
                        'url': url,
                        'error': 'No content extracted'
                    })
                    continue

                # Chunk the content
                chunks = self.chunker.chunk_text(content, url, crawled_data.get('title', ''))

                # Convert to TextChunk objects
                for chunk_data in chunks:
                    chunk = TextChunk(**chunk_data)
                    chunk.validate()
                    all_chunks.append(chunk)

                processed_urls.append(url)

            except Exception as e:
                error_count += 1
                error_details.append({
                    'url': url,
                    'error': str(e)
                })
                print(f"Error processing {url}: {str(e)}")

        end_time = datetime.now()

        # Determine status
        if error_count == 0:
            status = 'success'
        elif error_count == len(urls):
            status = 'failed'
        else:
            status = 'partial'

        # Create crawl result
        crawl_result = CrawlResult(
            crawl_id=crawl_id,
            source_url=urls[0] if urls else "",
            status=status,
            start_time=start_time,
            end_time=end_time,
            pages_processed=len(processed_urls),
            total_chunks=len(all_chunks),
            error_count=error_count,
            processed_urls=processed_urls,
            error_details=error_details,
            incremental=incremental
        )

        crawl_result.validate()
        return crawl_result, all_chunks

    def process_urls_incremental(self, urls: List[str], existing_chunks: List[TextChunk] = None, chunk_size: int = None, overlap_percentage: float = None) -> CrawlResult:
        """Process a list of URLs with incremental update detection."""
        try:
            if chunk_size is not None:
                self.settings.chunk_size = chunk_size
            if overlap_percentage is not None:
                self.settings.overlap_percentage = overlap_percentage

            crawl_id = f"crawl_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()

            all_chunks = []
            processed_urls = []
            error_count = 0
            error_details = []

            for url in urls:
                try:
                    print(f"Processing URL incrementally: {url}")
                    # Crawl the URL
                    crawled_data = self.crawler.crawl_single_url(url)

                    if not crawled_data:
                        error_count += 1
                        error_details.append({
                            'url': url,
                            'error': 'Failed to crawl URL'
                        })
                        continue

                    # Extract text content
                    content = crawled_data.get('content', '')
                    if not content:
                        error_count += 1
                        error_details.append({
                            'url': url,
                            'error': 'No content extracted'
                        })
                        continue

                    # Chunk the content
                    chunks = self.chunker.chunk_text(content, url, crawled_data.get('title', ''))

                    # Convert to TextChunk objects
                    for chunk_data in chunks:
                        chunk = TextChunk(**chunk_data)
                        chunk.validate()
                        all_chunks.append(chunk)

                    processed_urls.append(url)

                except Exception as e:
                    error_count += 1
                    error_details.append({
                        'url': url,
                        'error': str(e)
                    })
                    print(f"Error processing {url}: {str(e)}")

            # Detect changes if existing chunks provided
            unchanged_count = 0
            updated_count = 0

            if existing_chunks:
                changes = self._detect_content_changes(all_chunks, existing_chunks)
                unchanged_count = len(changes['unchanged'])
                updated_count = len(changes['updated'])
                # For incremental processing, we might only want to process changed/new content
                # For now, we'll process all but track the changes

            end_time = datetime.now()

            # Determine status
            if error_count == 0:
                status = 'success'
            elif error_count == len(urls):
                status = 'failed'
            else:
                status = 'partial'

            # Create crawl result with incremental data
            crawl_result = CrawlResult(
                crawl_id=crawl_id,
                source_url=urls[0] if urls else "",
                status=status,
                start_time=start_time,
                end_time=end_time,
                pages_processed=len(processed_urls),
                total_chunks=len(all_chunks),
                error_count=error_count,
                processed_urls=processed_urls,
                error_details=error_details,
                incremental=True,
                updated_chunks=updated_count,
                unchanged_chunks=unchanged_count
            )

            crawl_result.validate()
            return crawl_result
        except Exception as e:
            raise Exception(f"Error in incremental processing: {str(e)}")

    def validate_url_access(self, url: str) -> bool:
        """Validate that a URL is accessible."""
        try:
            response = self.crawler.session.head(url, timeout=self.settings.timeout_seconds)
            return response.status_code < 400
        except Exception:
            return False