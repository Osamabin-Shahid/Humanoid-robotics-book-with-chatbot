from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AgentQuery(BaseModel):
    """
    A natural language question or request submitted by the user to the RAG agent
    """

    query_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the query"
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The natural language query text"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the query was submitted"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional query metadata (user context, etc.)"
    )

    class Config:
        # Allow arbitrary types for datetime
        arbitrary_types_allowed = True

    @classmethod
    def create(cls, text: str, metadata: Optional[Dict[str, Any]] = None) -> 'AgentQuery':
        """
        Create a new AgentQuery instance.

        Args:
            text: The query text
            metadata: Optional metadata dictionary

        Returns:
            AgentQuery: New instance with generated ID and timestamp
        """
        return cls(text=text, metadata=metadata)


class RetrievedChunk(BaseModel):
    """
    Text segments from the book content that are semantically relevant to the user query
    """

    chunk_id: str = Field(
        ...,
        description="Unique identifier for the text chunk"
    )
    content_text: str = Field(
        ...,
        min_length=1,
        description="The actual text content"
    )
    source_url: str = Field(
        ...,
        description="URL or reference to the original source"
    )
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score indicating relevance to the query"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata (section, chapter, etc.)"
    )

    @classmethod
    def create(
        cls,
        chunk_id: str,
        content_text: str,
        source_url: str,
        similarity_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'RetrievedChunk':
        """
        Create a new RetrievedChunk instance.

        Args:
            chunk_id: Unique identifier for the chunk
            content_text: The actual text content
            source_url: Reference to the original source
            similarity_score: Relevance score between 0 and 1
            metadata: Optional metadata dictionary

        Returns:
            RetrievedChunk: New instance
        """
        return cls(
            chunk_id=chunk_id,
            content_text=content_text,
            source_url=source_url,
            similarity_score=similarity_score,
            metadata=metadata
        )


class AgentResponse(BaseModel):
    """
    The generated answer produced by the LLM based on the retrieved content and user query
    """

    response_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the response"
    )
    query_id: str = Field(
        ...,
        description="Reference to the original query"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="The generated response content"
    )
    retrieved_chunks: list[RetrievedChunk] = Field(
        default_factory=list,
        description="List of chunks used to generate the response"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the response was generated"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence level in the response accuracy"
    )

    class Config:
        # Allow arbitrary types for datetime and complex objects
        arbitrary_types_allowed = True

    @classmethod
    def create(
        cls,
        query_id: str,
        content: str,
        retrieved_chunks: list[RetrievedChunk],
        confidence_score: float = 0.0
    ) -> 'AgentResponse':
        """
        Create a new AgentResponse instance.

        Args:
            query_id: Reference to the original query
            content: The generated response content
            retrieved_chunks: List of chunks used to generate the response
            confidence_score: Confidence level between 0 and 1

        Returns:
            AgentResponse: New instance with generated ID and timestamp
        """
        return cls(
            query_id=query_id,
            content=content,
            retrieved_chunks=retrieved_chunks,
            confidence_score=confidence_score
        )