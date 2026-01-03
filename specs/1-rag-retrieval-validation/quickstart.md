# Quickstart Guide: RAG Retrieval and Validation

**Feature**: 1-rag-retrieval-validation
**Created**: 2025-12-27

## Prerequisites

- Python 3.9 or higher
- Access to Qdrant Cloud instance with existing collection
- Cohere API key
- Environment file (`.env`) with required configuration

## Setup

### 1. Environment Configuration
Create a `.env` file with the following variables:
```
QDRANT_URL=https://your-qdrant-instance.com
QDRANT_API_KEY=your_api_key
QDRANT_COLLECTION_NAME=your_collection_name
COHERE_API_KEY=your_cohere_api_key
```

### 2. Installation
```bash
pip install qdrant-client cohere python-dotenv pydantic fastapi uvicorn
```

### 3. Verify Configuration
```python
from src.config.settings import Settings
settings = Settings()
print(f"Qdrant URL: {settings.qdrant_url}")
print(f"Cohere API configured: {bool(settings.cohere_api_key)}")
```

## Basic Usage

### 1. Perform a Semantic Search
```python
from src.services.retrieval_service import RetrievalService
from src.config.settings import Settings

settings = Settings()
retrieval_service = RetrievalService(settings)

# Search for relevant content
query = "What are the key components of humanoid robotics?"
results = retrieval_service.retrieve(query, limit=5, min_score=0.5)

for result in results:
    print(f"Content: {result.content_text[:100]}...")
    print(f"Source: {result.source_url}")
    print(f"Score: {result.similarity_score}")
```

### 2. Validate Retrieved Results
```python
from src.services.validation_service import ValidationService

validation_service = ValidationService(settings)

# Validate a specific result
validation_report = validation_service.validate_result(
    result_id="result_123",
    expected_content="humanoid robotics components"
)

print(f"Alignment valid: {validation_report.alignment_valid}")
print(f"Overall score: {validation_report.overall_score}")
```

## API Usage

### Start the API Server
```bash
uvicorn main_api:app --host 0.0.0.0 --port 8000
```

### Query the API
```bash
curl -X POST http://localhost:8000/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain ROS 2 foundations",
    "limit": 3,
    "min_score": 0.6
  }'
```

### Validate Results via API
```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": "result_123",
    "expected_content": "ROS 2 concepts"
  }'
```

## Validation Workflow

1. **Query Content**: Submit natural language queries to retrieve relevant chunks
2. **Review Results**: Examine similarity scores and metadata alignment
3. **Validate Quality**: Use validation service to assess result quality
4. **Log Operations**: Ensure all operations are logged for reproducibility
5. **Verify Pipeline**: Confirm end-to-end functionality from storage to retrieval

## Common Operations

### Retrieve and Validate in One Step
```python
# Get results and validate them automatically
results_with_validation = retrieval_service.retrieve_and_validate(
    query="Your query here",
    limit=5
)

for result in results_with_validation:
    print(f"Content: {result.content_text}")
    print(f"Validation: {result.validation_report.overall_score}")
```

### Check Pipeline Integrity
```python
from src.services.pipeline_service import PipelineService

pipeline_service = PipelineService(settings)
integrity_check = pipeline_service.verify_store_to_retrieve()

print(f"Pipeline integrity: {integrity_check.status}")
print(f"Matching results: {integrity_check.matching_count}")
```

## Troubleshooting

### Common Issues
- **Connection errors**: Verify Qdrant URL and API key in `.env`
- **No results**: Check that the collection contains data and query is appropriate
- **Low quality results**: Adjust similarity score threshold or re-examine embeddings

### Validation Failures
- **Metadata misalignment**: Verify that stored content matches source URLs
- **Low coherence**: Review chunking strategy and embedding quality
- **Validation timeout**: Check external API availability