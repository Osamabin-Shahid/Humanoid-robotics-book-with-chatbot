# Research: RAG URL Pipeline

## Overview
Research for the RAG URL ingestion pipeline that crawls deployed book websites, extracts clean text, generates Cohere embeddings, and stores in Qdrant Cloud.

## Decision: Python Project Structure
**Rationale**: Following the user's requirement to initialize the project using `uv` and create a `backend/` directory with a single `main.py` entry file. This structure provides a clean separation for the RAG pipeline backend.

**Alternatives considered**:
- Monorepo with frontend/backend: Not needed as this is a backend-only service
- Standalone package: Less organization than modular approach
- Microservices: Overkill for single pipeline function

## Decision: Dependency Management with uv
**Rationale**: The user specifically requested using `uv` as the package manager, which is a modern, fast Python package manager that offers faster dependency resolution than pip.

**Alternatives considered**:
- pip + venv: Standard but slower than uv
- Poetry: Good but user specified uv
- Conda: More complex than needed for this project

## Decision: Text Extraction Approach
**Rationale**: Using BeautifulSoup4 with Requests for initial crawling and text extraction, with potential fallback to Selenium for JavaScript-heavy sites. This provides a good balance of performance and capability.

**Alternatives considered**:
- Selenium only: Slower, more resource intensive
- Playwright: More modern but potentially overkill for most sites
- Scrapy: More complex framework than needed for this use case

## Decision: Chunking Strategy
**Rationale**: Using configurable chunk size (default 512 tokens) with 20% overlap as specified in the requirements. This provides good context for semantic search while maintaining retrieval precision.

**Alternatives considered**:
- Fixed chunk sizes: Less flexibility
- Sentence-based chunking: May not optimize for embedding models
- Paragraph-based: May create chunks too large for optimal retrieval

## Decision: Cohere Embedding Models
**Rationale**: Using Cohere's latest supported embedding model as specified in constraints. Cohere models are known for good performance on semantic search tasks.

**Alternatives considered**:
- OpenAI embeddings: Not specified in requirements
- Sentence Transformers: Self-hosted but user specified Cohere
- Hugging Face models: Self-hosted but user specified Cohere

## Decision: Qdrant Cloud Integration
**Rationale**: Using Qdrant Cloud (Free Tier) as specified in the constraints. Qdrant is a purpose-built vector database with good performance for semantic search.

**Alternatives considered**:
- Pinecone: Alternative vector database but user specified Qdrant
- Weaviate: Alternative vector database but user specified Qdrant
- Self-hosted Qdrant: More complex deployment than cloud

## Decision: Environment Configuration
**Rationale**: Loading Cohere and Qdrant credentials from `.env` file as specified in requirements. This provides secure credential management while maintaining flexibility.

**Alternatives considered**:
- Hardcoded credentials: Insecure
- Command-line arguments: Visible in process lists
- Configuration files: Less secure than environment variables