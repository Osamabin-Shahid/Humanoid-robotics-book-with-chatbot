# Data Model: RAG Retrieval and Validation

**Feature**: 1-rag-retrieval-validation
**Created**: 2025-12-27

## Entities

### RetrievalResult
**Description**: Represents a single retrieved result from the semantic search

**Fields**:
- `result_id`: string (required) - Unique identifier for this result
- `query_text`: string (required) - The original query text
- `content_text`: string (required) - The retrieved text chunk content
- `source_url`: string (required) - URL of the original document
- `similarity_score`: float (required) - Semantic similarity score (0.0-1.0)
- `chunk_id`: string (required) - ID of the original text chunk
- `created_at`: datetime (required) - When the result was retrieved
- `validation_score`: float (optional) - Score from validation process
- `metadata`: object (optional) - Additional metadata from the original chunk

**Relationships**:
- Associated with one Query
- Contains reference to original source document

### Query
**Description**: Represents a user query for content retrieval

**Fields**:
- `query_id`: string (required) - Unique identifier for the query
- `text`: string (required) - The natural language query text
- `timestamp`: datetime (required) - When the query was made
- `limit`: integer (optional) - Maximum number of results to return (default: 10)
- `min_score`: float (optional) - Minimum similarity score threshold (default: 0.5)
- `parameters`: object (optional) - Additional query parameters

**Relationships**:
- Contains multiple RetrievalResult entities
- Associated with user session (if applicable)

### ValidationReport
**Description**: Represents the validation results for a retrieval operation

**Fields**:
- `validation_id`: string (required) - Unique identifier for the validation
- `result_id`: string (required) - ID of the result being validated
- `alignment_valid`: boolean (required) - Whether metadata aligns with content
- `metadata_correct`: boolean (required) - Whether metadata is accurate
- `content_coherent`: boolean (required) - Whether content is coherent
- `overall_score`: float (required) - Overall validation score (0.0-1.0)
- `validation_timestamp`: datetime (required) - When validation was performed
- `issues_found`: array of strings (optional) - List of validation issues

**Relationships**:
- Associated with one RetrievalResult
- Contains validation details

### LogEntry
**Description**: Represents a logged operation for reproducibility

**Fields**:
- `log_id`: string (required) - Unique identifier for the log entry
- `operation_type`: string (required) - Type of operation (query, validation, etc.)
- `timestamp`: datetime (required) - When the operation occurred
- `query_id`: string (optional) - ID of associated query
- `result_ids`: array of strings (optional) - IDs of associated results
- `parameters`: object (optional) - Operation parameters
- `status`: string (required) - Operation status (success, error, etc.)
- `details`: object (optional) - Additional operation details

**Relationships**:
- May reference Query and RetrievalResult entities
- Contains full operation context

## Validation Rules

### RetrievalResult
- `similarity_score` must be between 0.0 and 1.0
- `content_text` must not be empty
- `source_url` must be a valid URL format
- `result_id` must be unique within the system

### Query
- `text` must not be empty
- `limit` must be between 1 and 100
- `min_score` must be between 0.0 and 1.0

### ValidationReport
- `overall_score` must be between 0.0 and 1.0
- All boolean validation fields must be present
- `result_id` must reference an existing RetrievalResult

### LogEntry
- `operation_type` must be one of: "query", "validation", "retrieval", "error"
- `timestamp` must be in ISO 8601 format
- `status` must be one of: "success", "error", "partial", "timeout"