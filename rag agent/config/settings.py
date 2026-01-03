import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """
    Configuration settings for the RAG agent system.
    Loads configuration from environment variables.
    """

    # Qdrant configuration
    qdrant_url: str = Field(
        default=...,
        description="URL for Qdrant Cloud instance"
    )
    qdrant_api_key: str = Field(
        default=...,
        description="API key for Qdrant Cloud"
    )
    qdrant_collection_name: str = Field(
        default="book_content",
        description="Name of the collection containing book content embeddings"
    )

    # Gemini API configuration
    gemini_api_key: str = Field(
        default=...,
        description="Google Gemini API key for response generation"
    )
    gemini_model: str = Field(
        default="gemini-pro",
        description="Gemini model to use for response generation"
    )

    # Cohere API configuration (for query embeddings - matching stored embedding model)
    cohere_api_key: str = Field(
        default=...,
        description="Cohere API key for generating query embeddings compatible with stored vectors"
    )

    # Additional Qdrant configuration options
    qdrant_collection_exists_check: bool = Field(
        default=True,
        description="Whether to verify collection exists on startup"
    )

    # Agent configuration
    max_chunks_to_retrieve: int = Field(
        default=5,
        description="Maximum number of chunks to retrieve for context"
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for retrieved chunks"
    )

    class Config:
        # Allow environment variable names to be in different cases
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def load_from_env(cls) -> 'Settings':
        """
        Load settings from environment variables.

        Returns:
            Settings: Configuration object with values loaded from environment
        """
        return cls(
            qdrant_url=os.getenv("QDRANT_URL", ""),
            qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
            qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "book_content"),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-pro"),
            cohere_api_key=os.getenv("COHERE_API_KEY", ""),
            qdrant_collection_exists_check=os.getenv("QDRANT_COLLECTION_EXISTS_CHECK", "true").lower() == "true",
            max_chunks_to_retrieve=int(os.getenv("MAX_CHUNKS_TO_RETRIEVE", "5")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
        )

# Global settings instance
settings = Settings.load_from_env()