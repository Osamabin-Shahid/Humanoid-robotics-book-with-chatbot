# Quickstart: RAG URL Pipeline

## Overview
Quick setup guide for the RAG URL ingestion pipeline that crawls deployed book websites, extracts clean text, generates Cohere embeddings, and stores in Qdrant Cloud.

## Prerequisites
- Python 3.11 or higher
- `uv` package manager installed
- Access to Cohere API (API key)
- Access to Qdrant Cloud (URL and API key)

## Setup

### 1. Clone and Navigate to Project
```bash
# If this is part of a larger repository
cd backend
```

### 2. Install Dependencies with uv
```bash
# Initialize the project with uv
uv init

# Or if starting from scratch:
mkdir backend && cd backend
uv init
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv pytest
```

### 3. Environment Configuration
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Update `.env` with your credentials:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
```

### 4. Project Structure
After setup, your project should look like:
```
backend/
├── pyproject.toml
├── .env
├── .env.example
├── main.py
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── website_crawler.py
│   │   └── text_extractor.py
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── models.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py
│   │   └── models.py
│   ├── chunking/
│   │   ├── __init__.py
│   │   └── text_chunker.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
└── tests/
    ├── __init__.py
    ├── test_crawler.py
    ├── test_embedding.py
    ├── test_storage.py
    ├── test_chunking.py
    └── conftest.py
```

## Usage

### Run the Ingestion Pipeline
```bash
# Run the main pipeline with website URLs
python main.py --urls "https://example-book.com" "https://another-book.com"

# Or with specific configuration
python main.py --urls "https://example-book.com" --chunk-size 512 --overlap 0.2
```

### Run Tests
```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_crawler.py
pytest tests/test_embedding.py
```

## Configuration Options
- `--urls`: List of website URLs to process (required)
- `--chunk-size`: Size of text chunks in tokens (default: 512)
- `--overlap`: Overlap percentage between chunks (default: 0.2)
- `--collection`: Qdrant collection name (default: "book_embeddings")

## Example Usage
```bash
# Process a single website
python main.py --urls "https://my-book-website.com"

# Process multiple websites with custom chunk size
python main.py --urls "https://book1.com" "https://book2.com" --chunk-size 1024
```

## Troubleshooting

### Common Issues
1. **API Rate Limits**: The pipeline includes built-in rate limiting, but if you encounter issues, adjust the configuration parameters.

2. **Authentication Errors**: Verify that your Cohere and Qdrant credentials in `.env` are correct.

3. **Website Access**: Some websites may have robots.txt restrictions or require authentication. The crawler will handle these gracefully with appropriate logging.

### Verification
To verify the pipeline worked correctly:
1. Check the logs for successful completion
2. Verify vectors were stored in Qdrant by querying the collection
3. Run the verification tests: `pytest tests/test_storage.py`