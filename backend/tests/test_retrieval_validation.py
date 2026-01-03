#!/usr/bin/env python3
"""
Test Script for RAG Retrieval and Validation

This script provides simple test queries to verify basic retrieval functionality
for the RAG retrieval and validation system.
"""
import sys
import os
import logging
from typing import List

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.search_service import SemanticSearchService
from src.embedding.query_generator import QueryEmbeddingGenerator


def setup_logging():
    """Set up logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_basic_retrieval():
    """Test basic retrieval functionality."""
    print("Testing basic retrieval functionality...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test query
        query_text = "What are the foundations of ROS 2?"
        print(f"Query: {query_text}")

        # Perform retrieval
        results = retrieval_service.retrieve(query_text, limit=3, min_score=0.1)

        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result.similarity_score:.3f}")
            print(f"     Source: {result.source_url}")
            print(f"     Content preview: {result.content_text[:100]}...")
            print(f"     Chunk ID: {result.chunk_id}")
            print()

        print("✅ Basic retrieval test passed!")
        return True

    except Exception as e:
        print(f"❌ Basic retrieval test failed: {e}")
        return False


def test_query_embedding_generation():
    """Test query embedding generation."""
    print("Testing query embedding generation...")

    try:
        # Initialize the settings and query generator
        settings = Settings()
        query_generator = QueryEmbeddingGenerator(settings)

        # Test query
        query_text = "Humanoid robotics components"
        print(f"Query: {query_text}")

        # Generate embedding
        embedding_vector = query_generator.generate_query_embedding(query_text)
        print(f"Generated embedding with {embedding_vector.dimension} dimensions")
        print(f"Vector ID: {embedding_vector.vector_id}")

        # Get just the vector data
        vector_data = query_generator.get_query_embedding(query_text)
        print(f"Vector data length: {len(vector_data)}")

        print("SUCCESS: Query embedding generation test passed!")
        return True

    except Exception as e:
        print(f"FAILED: Query embedding generation test failed: {e}")
        return False


def test_semantic_search():
    """Test semantic search functionality."""
    print("Testing semantic search functionality...")

    try:
        # Initialize the settings and search service
        settings = Settings()
        search_service = SemanticSearchService(settings)

        # Test query
        query_text = "Explain cognitive planning for humanoid robots"
        print(f"Query: {query_text}")

        # Perform search
        results = search_service.search(query_text, limit=2, min_score=0.1)

        print(f"Found {len(results)} similar chunks:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Similarity: {result.similarity_score:.3f}")
            print(f"     Source: {result.source_url}")
            print(f"     Content: {result.content_text[:80]}...")
            print()

        print("✅ Semantic search test passed!")
        return True

    except Exception as e:
        print(f"❌ Semantic search test failed: {e}")
        return False


def test_retrieval_with_validation():
    """Test retrieval with validation."""
    print("Testing retrieval with validation...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test query
        query_text = "What is Isaac Sim?"
        print(f"Query: {query_text}")

        # Perform retrieval with validation
        results = retrieval_service.retrieve_and_validate(query_text, limit=2, min_score=0.1)

        print(f"Found {len(results)} validated results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result.similarity_score:.3f}")
            print(f"     Source: {result.source_url}")
            print(f"     Content: {result.content_text[:80]}...")
            print()

        print("✅ Retrieval with validation test passed!")
        return True

    except Exception as e:
        print(f"❌ Retrieval with validation test failed: {e}")
        return False


def test_quality_validation():
    """Test quality validation of retrieval results."""
    print("Testing quality validation of retrieval results...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test query
        query_text = "What are the key components of a humanoid robot?"
        expected_keywords = ["robot", "components", "humanoid", "actuator", "sensor"]
        print(f"Query: {query_text}")
        print(f"Expected keywords: {expected_keywords}")

        # Perform quality validation
        validation_report = retrieval_service.validate_retrieval_quality(
            query_text, expected_keywords, limit=3
        )

        print(f"Validation report:")
        print(f"  - Total results: {validation_report['total_results']}")
        print(f"  - Relevant results: {validation_report['relevant_results']}")
        print(f"  - Quality score: {validation_report['quality_score']:.2f}")
        print(f"  - Relevance percentage: {validation_report['relevance_percentage']:.1f}%")

        print("✅ Quality validation test passed!")
        return True

    except Exception as e:
        print(f"❌ Quality validation test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("Starting RAG Retrieval and Validation tests...\n")

    tests = [
        test_query_embedding_generation,
        test_semantic_search,
        test_basic_retrieval,
        test_retrieval_with_validation,
        test_quality_validation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print("-" * 50)
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The RAG retrieval system is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    setup_logging()

    # Check if required environment variables are set
    try:
        test_settings = Settings()
        if not test_settings.cohere_api_key or not test_settings.qdrant_url or not test_settings.qdrant_api_key:
            print("❌ Environment variables not properly configured!")
            print("Please ensure COHERE_API_KEY, QDRANT_URL, and QDRANT_API_KEY are set in your .env file.")
            sys.exit(1)

        print("Environment variables loaded successfully.")
        print(f"Qdrant URL: {test_settings.qdrant_url}")
        print(f"Qdrant Collection: {test_settings.qdrant_collection_name}")
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        sys.exit(1)
    print()

    success = run_all_tests()
    sys.exit(0 if success else 1)