"""
Local execution utilities for testing the RAG agent.
Provides functions to facilitate local testing and development.
"""

import sys
import os
import time
from typing import List, Optional, Dict, Any
from ..models.agent_query import AgentQuery, RetrievedChunk, AgentResponse
from ..agents.rag_agent import rag_agent
from ..retrieval.qdrant_client import qdrant_client
from ..services.response_generator import response_generator
from ..config.settings import settings


class LocalExecutionService:
    """
    Service providing utilities for local execution and testing of the RAG agent.
    """

    def __init__(self):
        """
        Initialize the local execution service.
        """
        self.agent = rag_agent

    def run_test_query(self, query_text: str) -> AgentResponse:
        """
        Run a test query through the RAG agent in local execution mode.

        Args:
            query_text: The query text to test

        Returns:
            AgentResponse with the result of the query
        """
        print(f"Running test query: '{query_text}'")
        start_time = time.time()

        # Process the query using the agent
        response = self.agent.process_query(query_text)

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"Query processed in {processing_time:.2f} seconds")
        print(f"Response: {response.content}")
        print(f"Confidence: {response.confidence_score:.2f}")
        print(f"Retrieved {len(response.retrieved_chunks)} chunks")

        return response

    def run_batch_queries(self, queries: List[str]) -> List[AgentResponse]:
        """
        Run multiple test queries in batch mode.

        Args:
            queries: List of query strings to test

        Returns:
            List of AgentResponse objects for each query
        """
        responses = []
        print(f"Running batch of {len(queries)} queries...")

        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}/{len(queries)}: {query}")
            response = self.run_test_query(query)
            responses.append(response)

        return responses

    def test_connection_health(self) -> Dict[str, Any]:
        """
        Test the health of all connections and services.

        Returns:
            Dictionary with health status of all services
        """
        print("Testing connection health...")

        # Test RAG agent health
        health_status = self.agent.check_health()
        print(f"RAG Agent Health: {health_status}")

        # Test Qdrant connection specifically
        try:
            qdrant_healthy = qdrant_client.check_connection()
            print(f"Qdrant Connection: {'✓ Healthy' if qdrant_healthy else '✗ Unhealthy'}")
            health_status['qdrant_direct_check'] = qdrant_healthy
        except Exception as e:
            print(f"Qdrant Connection: ✗ Error - {str(e)}")
            health_status['qdrant_direct_check'] = False

        return health_status

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the local execution environment.

        Returns:
            Dictionary with system information
        """
        info = {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "settings": {
                "qdrant_collection_name": settings.qdrant_collection_name,
                "max_chunks_to_retrieve": settings.max_chunks_to_retrieve,
                "similarity_threshold": settings.similarity_threshold,
                "gemini_model": settings.gemini_model
            },
            "configured_services": {
                "has_qdrant_url": bool(settings.qdrant_url),
                "has_qdrant_api_key": bool(settings.qdrant_api_key),
                "has_gemini_api_key": bool(settings.gemini_api_key),
                "has_cohere_api_key": bool(settings.cohere_api_key)
            }
        }

        return info

    def run_performance_test(
        self,
        query: str,
        iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Run a performance test by executing the same query multiple times.

        Args:
            query: The query to test
            iterations: Number of times to run the query

        Returns:
            Dictionary with performance metrics
        """
        print(f"Running performance test with {iterations} iterations...")

        times = []
        responses = []

        for i in range(iterations):
            start_time = time.time()
            response = self.run_test_query(query)
            end_time = time.time()

            query_time = end_time - start_time
            times.append(query_time)
            responses.append(response)

            print(f"Iteration {i+1}: {query_time:.2f}s")

        # Calculate metrics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        metrics = {
            "iterations": iterations,
            "query": query,
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "total_time": sum(times),
            "responses": responses
        }

        print(f"\nPerformance Metrics:")
        print(f"  Average time: {avg_time:.2f}s")
        print(f"  Min time: {min_time:.2f}s")
        print(f"  Max time: {max_time:.2f}s")

        return metrics

    def validate_response_quality(
        self,
        query: str,
        expected_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate the quality of a response by checking for expected content.

        Args:
            query: The query to test
            expected_keywords: Optional list of keywords that should appear in the response

        Returns:
            Dictionary with validation results
        """
        response = self.run_test_query(query)

        validation_result = {
            "query": query,
            "response_length": len(response.content),
            "confidence_score": response.confidence_score,
            "num_chunks_retrieved": len(response.retrieved_chunks),
            "chunks_similarity_scores": [c.similarity_score for c in response.retrieved_chunks]
        }

        if expected_keywords:
            found_keywords = []
            response_lower = response.content.lower()

            for keyword in expected_keywords:
                if keyword.lower() in response_lower:
                    found_keywords.append(keyword)

            validation_result["expected_keywords"] = expected_keywords
            validation_result["found_keywords"] = found_keywords
            validation_result["keyword_match_ratio"] = len(found_keywords) / len(expected_keywords) if expected_keywords else 0

        return validation_result


# Global local execution service instance
local_execution_service = LocalExecutionService()