# Data Model: RAG Agent

## Entities

### Agent Query
**Description**: A natural language question or request submitted by the user to the RAG agent

**Fields**:
- `query_id`: Unique identifier for the query
- `text`: The natural language query text
- `timestamp`: When the query was submitted
- `metadata`: Additional query metadata (user context, etc.)

**Validation Rules**:
- Query text must not be empty
- Query text must be less than 1000 characters
- Query must be in a supported language

### Retrieved Chunks
**Description**: Text segments from the book content that are semantically relevant to the user query

**Fields**:
- `chunk_id`: Unique identifier for the text chunk
- `content_text`: The actual text content
- `source_url`: URL or reference to the original source
- `similarity_score`: Score indicating relevance to the query
- `metadata`: Additional metadata (section, chapter, etc.)

**Validation Rules**:
- Content text must not be empty
- Similarity score must be between 0 and 1
- Source reference must be valid

### Agent Response
**Description**: The generated answer produced by the LLM based on the retrieved content and user query

**Fields**:
- `response_id`: Unique identifier for the response
- `query_id`: Reference to the original query
- `content`: The generated response content
- `retrieved_chunks`: List of chunks used to generate the response
- `timestamp`: When the response was generated
- `confidence_score`: Confidence level in the response accuracy

**Validation Rules**:
- Response content must not be empty
- Must reference at least one retrieved chunk
- Confidence score must be between 0 and 1

## Relationships
- One Agent Query can generate one Agent Response
- One Agent Query can retrieve multiple Retrieved Chunks
- One Agent Response uses multiple Retrieved Chunks as context