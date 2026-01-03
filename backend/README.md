# RAG URL Pipeline

RAG URL ingestion pipeline for crawling websites, generating embeddings, and storing in Qdrant.

## Overview

This project implements a RAG (Retrieval-Augmented Generation) URL ingestion pipeline that:
- Crawls deployed book websites to extract clean text content
- Generates semantic embeddings using Cohere models
- Stores vectors with metadata in Qdrant Cloud
- Supports configurable chunking with overlap for optimal RAG retrieval
- Handles API rate limits gracefully and maintains data integrity

## Prerequisites

- Python 3.11 or higher
- uv package manager (or pip)
- Cohere API key
- Qdrant Cloud account and API key

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   # Or if using uv:
   uv pip install cohere qdrant-client beautifulsoup4 requests python-dotenv pytest fastapi uvicorn
   ```
4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
5. Update `.env` with your Cohere and Qdrant credentials

## Usage

### Command Line Interface

Process websites and generate embeddings:

```bash
python main.py --urls "https://example-book.com" "https://another-book.com" --chunk-size 512 --overlap 0.2 --store
```

Options:
- `--urls`: List of website URLs to process (required)
- `--chunk-size`: Size of text chunks in tokens (default: 512)
- `--overlap`: Overlap percentage between chunks (default: 0.2)
- `--store`: Store embeddings in Qdrant (default: False)

### API Server

Run the API server:

```bash
python main_api.py
```

Or with uvicorn:

```bash
uvicorn main_api:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:
- `POST /api/v1/crawl` - Crawl websites and generate embeddings
- `POST /api/v1/embed` - Generate embeddings for text chunks
- `GET /api/v1/health` - Health check
- `GET /api/v1/ready` - Readiness check

## Configuration

The pipeline can be configured using environment variables in the `.env` file:

```env
# Cohere API Configuration
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=embed-multilingual-v2.0

# Qdrant Cloud Configuration
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=book_embeddings

# Pipeline Configuration
CHUNK_SIZE=512
OVERLAP_PERCENTAGE=0.2
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_PERIOD=60
TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

## Architecture

The pipeline is organized into the following modules:

- `src/crawler/` - Website crawling and text extraction
- `src/chunking/` - Text chunking with overlap
- `src/embedding/` - Cohere embedding generation
- `src/storage/` - Qdrant Cloud integration
- `src/services/` - Business logic orchestration
- `src/config/` - Configuration and settings
- `src/utils/` - Helper functions and utilities

## Testing

Run the tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## Performance

The pipeline is optimized to:
- Process 10,000 text chunks per hour
- Generate embeddings with processing time under 5 seconds per 1000 tokens
- Enable similarity search with response time under 100ms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

[Specify your license here]