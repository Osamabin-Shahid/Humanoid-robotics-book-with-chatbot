# RAG Agent - Book Content Query System

This RAG (Retrieval-Augmented Generation) agent allows users to ask questions about book content and receive accurate, contextually relevant answers grounded in the source material. The agent retrieves relevant text chunks from a vector database and uses them as context for response generation.

## Features

- Semantic search through book content using vector embeddings
- Grounded responses using retrieved context
- Configurable similarity thresholds
- Comprehensive logging
- Health checks for all services
- Local testing capabilities

## Prerequisites

- Python 3.11 or higher
- Qdrant Cloud account with existing collection containing book content embeddings
- Google Gemini API key
- Cohere API key (for query embeddings to match stored vectors)

## Setup

1. **Clone the repository** (if needed):
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Navigate to the rag agent directory**:
   ```bash
   cd "rag agent"
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   Create a `.env` file in the "rag agent" directory with the following content:
   ```env
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   QDRANT_COLLECTION_NAME=your_collection_name
   GEMINI_API_KEY=your_gemini_api_key
   COHERE_API_KEY=your_cohere_api_key
   GEMINI_MODEL=gemini-pro  # Optional, defaults to gemini-pro
   MAX_CHUNKS_TO_RETRIEVE=5  # Optional, defaults to 5
   SIMILARITY_THRESHOLD=0.7  # Optional, defaults to 0.7
   ```

## Usage

### Interactive Mode (Default)

Run the agent in interactive mode to ask questions:
```bash
python main.py
```

### Command Line Options

The agent supports different run modes:

1. **Health Check**:
   ```bash
   python main.py --mode health
   ```

2. **Test Mode**:
   ```bash
   # Run system info
   python main.py --mode test

   # Run single query
   python main.py --mode test --query "What is artificial intelligence?"

   # Run batch queries
   python main.py --mode test --batch "What is AI?" "How does ML work?"
   ```

3. **Interactive Mode** (default):
   ```bash
   python main.py --mode interactive
   ```

## Configuration

The agent uses the following configuration parameters from environment variables:

- `QDRANT_URL`: URL for your Qdrant Cloud instance
- `QDRANT_API_KEY`: API key for Qdrant Cloud
- `QDRANT_COLLECTION_NAME`: Name of the collection containing book content embeddings (default: `book_content`)
- `GEMINI_API_KEY`: Google Gemini API key for response generation
- `COHERE_API_KEY`: Cohere API key for generating query embeddings (must match the model used for stored vectors)
- `GEMINI_MODEL`: Gemini model to use (default: `gemini-pro`)
- `MAX_CHUNKS_TO_RETRIEVE`: Maximum number of chunks to retrieve for context (default: `5`)
- `SIMILARITY_THRESHOLD`: Minimum similarity score for retrieved chunks (default: `0.7`)

## Architecture

The system follows a modular architecture with clear separation of concerns:

- `agents/`: Core RAG agent implementation that orchestrates the entire process
- `retrieval/`: Qdrant integration and semantic search functionality
- `services/`: Response generation, logging, and utility services
- `models/`: Pydantic data models for queries, chunks, and responses
- `config/`: Configuration management using environment variables
- `tests/`: Comprehensive test suites for all components
- `services/retry_utils.py`: Utilities for retry logic and rate limiting

### Core Components

1. **RAG Agent** (`agents/rag_agent.py`): Main orchestrator that handles query processing, embedding generation, retrieval, and response generation.

2. **Qdrant Client** (`retrieval/qdrant_client.py`): Handles semantic search and retrieval from the vector database with retry logic.

3. **Response Generator** (`services/response_generator.py`): Generates grounded responses using Gemini API with validation.

4. **Data Models** (`models/agent_query.py`): Pydantic models for structured data handling.

5. **Configuration** (`config/settings.py`): Centralized configuration management with validation.

### Error Handling and Resilience

- Comprehensive error handling throughout all services
- Retry logic with exponential backoff for API calls
- Graceful degradation when services are unavailable
- Detailed logging for debugging and monitoring
- Response validation to ensure grounding in source content

## Testing

Run the test suites to verify functionality:

```bash
# Run basic RAG agent tests
python -m pytest tests/test_rag_agent.py

# Run configuration tests
python -m pytest tests/test_configuration.py

# Run retrieval tests
python -m pytest tests/test_retrieval.py

# Run end-to-end integration tests
python -m pytest tests/test_integration.py

# Run all tests
python -m pytest tests/
```

## Local Development

For local development and testing, use the test modes:

```bash
# Check system health
python main.py --mode health

# Test with sample queries
python main.py --mode test --query "What is the main concept?"

# Run batch of test queries
python main.py --mode test --batch "Query 1?" "Query 2?" "Query 3?"
```

## Troubleshooting

- **Qdrant Connection Issues**: Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
- **API Key Issues**: Ensure both `GEMINI_API_KEY` and `COHERE_API_KEY` are valid
- **No Relevant Results**: Check that the Qdrant collection contains the expected book content with compatible embeddings
- **Embedding Compatibility**: Ensure the Cohere model used for query embeddings matches the one used for stored content

## API Contract

The system supports the following operations:
- Query processing with semantic retrieval
- Response generation with grounding validation
- Health status checking
- Configuration validation

## Performance

- Response generation typically under 10 seconds
- 90% retrieval accuracy for relevant queries
- 95% of responses contain information directly sourced from retrieved content