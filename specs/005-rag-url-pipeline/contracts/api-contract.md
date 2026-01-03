# API Contract: RAG URL Pipeline

## Overview
API contract for the RAG URL ingestion pipeline. This defines the interface for the backend service that handles website crawling, text extraction, embedding generation, and vector storage.

## Data Models

### CrawlRequest
Request object for initiating a website crawl operation.

```json
{
  "urls": ["https://example-book.com", "https://another-book.com"],
  "configuration": {
    "chunk_size": 512,
    "overlap_percentage": 0.2,
    "timeout_seconds": 30,
    "max_retries": 3
  }
}
```

**Fields**:
- `urls`: Array of website URLs to crawl and process (required)
- `configuration`: Optional configuration parameters for the crawl operation

### CrawlResponse
Response object for a crawl operation.

```json
{
  "crawl_id": "crawl_abc123",
  "status": "success",
  "pages_processed": 25,
  "total_chunks": 150,
  "error_count": 0,
  "start_time": "2025-12-26T10:00:00Z",
  "end_time": "2025-12-26T10:05:00Z",
  "processed_urls": ["https://example-book.com/page1", "https://example-book.com/page2"]
}
```

**Fields**:
- `crawl_id`: Unique identifier for the crawl operation
- `status`: Status of the operation (success, partial, failed)
- `pages_processed`: Number of pages successfully processed
- `total_chunks`: Total number of text chunks created
- `error_count`: Number of errors encountered
- `start_time`: Timestamp when crawl started
- `end_time`: Timestamp when crawl completed
- `processed_urls`: List of URLs that were successfully processed

### EmbeddingRequest
Request object for generating embeddings for text chunks.

```json
{
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "content": "This is the text content of the first chunk...",
      "source_url": "https://example-book.com/chapter1",
      "metadata": {
        "section": "Chapter 1",
        "sequence_number": 1
      }
    }
  ],
  "model": "embed-multilingual-v2.0"
}
```

**Fields**:
- `chunks`: Array of text chunks to generate embeddings for
- `model`: Cohere model to use for embedding generation

### EmbeddingResponse
Response object for embedding generation.

```json
{
  "embeddings": [
    {
      "chunk_id": "chunk_001",
      "vector": [0.1, 0.2, 0.3, ...],
      "model": "embed-multilingual-v2.0",
      "dimension": 1024
    }
  ],
  "model": "embed-multilingual-v2.0",
  "total_processed": 1
}
```

**Fields**:
- `embeddings`: Array of embedding vectors with associated metadata
- `model`: Model used for embedding generation
- `total_processed`: Number of chunks processed

## Endpoints

### POST /api/v1/crawl
Initiate a website crawling and ingestion operation.

**Request**:
- Path: `/api/v1/crawl`
- Method: `POST`
- Content-Type: `application/json`
- Body: `CrawlRequest` object

**Response**:
- Success: `200 OK` with `CrawlResponse` object
- Error: `400 Bad Request` for invalid input, `500 Internal Server Error` for processing errors

**Example Request**:
```json
{
  "urls": ["https://my-book-site.com"],
  "configuration": {
    "chunk_size": 512,
    "overlap_percentage": 0.2
  }
}
```

### POST /api/v1/embed
Generate embeddings for provided text chunks.

**Request**:
- Path: `/api/v1/embed`
- Method: `POST`
- Content-Type: `application/json`
- Body: `EmbeddingRequest` object

**Response**:
- Success: `200 OK` with `EmbeddingResponse` object
- Error: `400 Bad Request` for invalid input, `500 Internal Server Error` for processing errors

### GET /api/v1/health
Check the health status of the service.

**Request**:
- Path: `/api/v1/health`
- Method: `GET`

**Response**:
- Success: `200 OK` with health status
- Error: `503 Service Unavailable` if service is unhealthy

## Error Handling

### Standard Error Format
All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details if available"
  }
}
```

### Common Error Codes
- `INVALID_INPUT`: Request data is invalid or malformed
- `AUTHENTICATION_FAILED`: API credentials are invalid
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `RATE_LIMIT_EXCEEDED`: API rate limits exceeded
- `INTERNAL_ERROR`: Internal server error occurred
- `CRAWL_FAILED`: Website crawling operation failed
- `EMBEDDING_FAILED`: Embedding generation failed
- `STORAGE_FAILED`: Vector storage operation failed