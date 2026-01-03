# Quickstart: RAG Agent using OpenAI Agent SDK

## Prerequisites

- Python 3.11 or higher
- Qdrant Cloud account with existing collection
- Google Gemini API key
- Git

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
   Create a `.env` file in the root directory with the following content:
   ```env
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   QDRANT_COLLECTION_NAME=your_collection_name
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Usage

### Running the Agent Locally

1. **Start the RAG agent**:
   ```bash
   python main.py
   ```

2. **Interact with the agent**:
   The agent will prompt for queries and provide responses based on the book content.

### Testing the Agent

1. **Run the tests**:
   ```bash
   python -m pytest tests/
   ```

2. **Test specific functionality**:
   ```bash
   python -m pytest tests/test_retrieval.py
   python -m pytest tests/test_rag_agent.py
   ```

## Configuration

The agent loads configuration from the `.env` file:
- `QDRANT_URL`: URL for Qdrant Cloud instance
- `QDRANT_API_KEY`: API key for Qdrant Cloud
- `QDRANT_COLLECTION_NAME`: Name of the collection containing book content embeddings
- `GEMINI_API_KEY`: Google Gemini API key for response generation

## Troubleshooting

- **Qdrant connection errors**: Verify QDRANT_URL and QDRANT_API_KEY are correct
- **Gemini API errors**: Check GEMINI_API_KEY is valid and API is enabled
- **No relevant results**: Ensure the Qdrant collection contains the expected book content