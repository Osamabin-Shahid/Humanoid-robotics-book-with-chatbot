# RAG Retrieval and Validation System

This system provides a comprehensive solution for retrieving and validating vectorized book content for RAG (Retrieval-Augmented Generation) pipelines. It allows AI engineers to retrieve relevant text chunks from Qdrant using semantic search, validate embedding quality and metadata alignment, verify chunking strategy effectiveness, and ensure the end-to-end pipeline functions correctly.

## Architecture

The system is organized into the following modules:

### Core Components

- **Configuration (`config/settings.py`)**: Manages environment variables and configuration for Qdrant Cloud and Cohere API
- **Data Models (`models/`)**: Defines data structures for retrieval results, queries, validation reports, and log entries
- **Services (`services/`)**: Business logic for logging, search, retrieval, validation, and pipeline operations
- **Embedding (`embedding/`)**: Handles query embedding generation using Cohere API
- **Storage (`storage/`)**: Qdrant Cloud integration for vector storage and retrieval
- **API (`api/`)**: FastAPI endpoints for retrieval and validation operations
- **Utilities (`utils/`)**: Helper functions including retry utilities

### Data Models

- `RetrievalResult`: Represents a single retrieval result with content, metadata, and similarity score
- `Query`: Defines query parameters and constraints
- `ValidationReport`: Contains validation results with issues and scores
- `LogEntry`: Captures operation logs for reproducibility

### Services

- `LoggingService`: Comprehensive logging for operations, errors, and effectiveness metrics
- `SemanticSearchService`: Performs semantic search using Cohere embeddings and Qdrant
- `RetrievalService`: Orchestrates the retrieval process with validation
- `ValidationService`: Validates metadata alignment, content quality, and chunk coherence
- `MetadataValidator`: Specific validation for metadata alignment
- `ContentValidator`: Specific validation for content quality
- `CoherenceValidator`: Validates chunk coherence and contextual meaning preservation
- `PipelineService`: End-to-end pipeline validation

## Configuration

The system uses environment variables for configuration:

```env
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=your_collection_name
COHERE_API_KEY=your_cohere_api_key
COHERE_MODEL=embed-multilingual-v2.0  # or your preferred model
```

## API Endpoints

### Retrieval Endpoints

- `POST /retrieve`: Retrieve relevant content based on query text
- `POST /retrieve-with-validation`: Retrieve content with validation reports
- `GET /health`: Health check endpoint

### Validation Endpoints

- `POST /validate-retrieval`: Validate retrieval quality
- `POST /validate-content`: Validate content quality
- `POST /validate-metadata`: Validate metadata alignment
- `POST /validate-coherence`: Validate chunk coherence
- `POST /validate-pipeline`: Validate pipeline integrity
- `GET /validation/health`: Validation service health check

## Usage Examples

### Basic Retrieval

```python
import requests

# Retrieve relevant content
response = requests.post("http://localhost:8000/retrieve", json={
    "query_text": "What are the key concepts in machine learning?",
    "limit": 10,
    "min_score": 0.1,
    "validate_results": False
})

results = response.json()
```

### Retrieval with Validation

```python
# Retrieve and validate content
response = requests.post("http://localhost:8000/retrieve-with-validation", json={
    "query_text": "Explain neural networks",
    "limit": 5,
    "min_score": 0.2,
    "validate_results": True
})

result = response.json()
```

## Validation Features

### Metadata Alignment Validation

Validates that stored embeddings properly align with their source URLs and metadata, including:
- Required metadata fields presence
- URL format validation
- Content-text alignment
- Consistency between result object and metadata

### Content Quality Validation

Validates the quality of retrieved content, including:
- Content length and completeness
- Encoding issues detection
- Repetition detection
- Readability scoring
- Relevance to query

### Chunk Coherence Validation

Validates that text chunks preserve contextual meaning, including:
- Sentence completeness
- Paragraph structure
- Chunking artifacts detection
- Context preservation scoring

### Pipeline Validation

Validates the entire RAG pipeline, including:
- Integrity of storage-retrieval process
- Reproducibility of results
- Chunking strategy effectiveness
- End-to-end functionality

## Error Handling and Retry Logic

The system implements comprehensive error handling with:

- **Retry Logic**: Exponential backoff for API failures (Cohere, Qdrant)
- **Rate Limiting**: Controls API call frequency
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Graceful Degradation**: Continues operation when possible despite partial failures

## Performance Considerations

- **Caching**: Results can be cached to improve response times
- **Batch Processing**: Multiple queries can be processed efficiently
- **Async Operations**: Non-blocking operations where possible
- **Resource Management**: Proper connection handling and cleanup

## Testing

The system includes comprehensive tests in the `tests/` directory:

- Unit tests for individual components
- Integration tests for end-to-end functionality
- Performance tests for retrieval speed
- Validation tests for accuracy

## Logging

All operations are logged with detailed metrics:

- Query execution times
- Retrieval effectiveness metrics
- Validation scores and issues
- Error details with context
- System health indicators

## Security

- API keys are loaded from environment variables
- SSL/TLS encryption for all external connections
- Input validation to prevent injection attacks
- Proper error message sanitization

## Monitoring and Observability

The system provides:

- Health check endpoints
- Performance metrics
- Error rate tracking
- Validation effectiveness reports
- Resource usage statistics