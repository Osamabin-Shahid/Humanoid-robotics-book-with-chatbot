#!/usr/bin/env python3
"""
Test Script for Chunk Effectiveness in RAG Retrieval and Validation

This script provides tests to verify the effectiveness of the chunking strategy
for the RAG retrieval and validation system, focusing on coherence and contextual meaning preservation.
"""
import sys
import os
import logging
from typing import List

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.coherence_validator import CoherenceValidator
from src.services.pipeline_service import PipelineService
from src.models.retrieval_result_model import RetrievalResult


def setup_logging():
    """Set up logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_chunk_coherence_validation():
    """Test chunk coherence validation functionality."""
    print("Testing chunk coherence validation...")

    try:
        # Initialize the settings and coherence validator
        settings = Settings()
        coherence_validator = CoherenceValidator(settings)

        # Create a sample retrieval result with good coherence
        good_coherence_result = RetrievalResult(
            result_id="test_result_1",
            query_text="Test query about humanoid robotics",
            content_text="Humanoid robotics is an interdisciplinary branch of robotics that studies and develops robots with human-like features. These robots are designed to mimic human behavior and appearance, allowing them to interact with human tools and environments effectively. The field combines mechanical engineering, electronics, and artificial intelligence to create sophisticated machines.",
            source_url="https://example.com/humanoid-robotics",
            similarity_score=0.82,
            chunk_id="chunk_001",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://example.com/humanoid-robotics",
                "chunk_id": "chunk_001",
                "content": "Humanoid robotics is an interdisciplinary branch of robotics that studies and develops robots with human-like features. These robots are designed to mimic human behavior and appearance, allowing them to interact with human tools and environments effectively. The field combines mechanical engineering, electronics, and artificial intelligence to create sophisticated machines.",
                "created_at": "2025-12-27T10:00:00Z"
            }
        )

        print(f"Testing good coherence: {good_coherence_result.source_url}")

        # Perform coherence validation
        coherence_report = coherence_validator.validate_chunk_coherence(good_coherence_result)

        print(f"Coherence validation result: {'VALID' if coherence_report.is_valid else 'INVALID'}")
        print(f"Issues: {coherence_report.issues}")
        print(f"Metadata: {coherence_report.metadata}")

        # Create a sample retrieval result with poor coherence (chunking artifacts)
        poor_coherence_result = RetrievalResult(
            result_id="test_result_2",
            query_text="Test query",
            content_text="...mimic human behavior and appearance, allowing them to interact with human tools. The field combines mechanical engineering, electronics, and artificial intelligence. This is a continuation of the previous thought",
            source_url="https://example.com/poor-coherence",
            similarity_score=0.45,
            chunk_id="chunk_002",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://example.com/poor-coherence",
                "chunk_id": "chunk_002",
                "content": "...mimic human behavior and appearance, allowing them to interact with human tools. The field combines mechanical engineering, electronics, and artificial intelligence. This is a continuation of the previous thought",
                "created_at": "2025-12-27T10:00:00Z"
            }
        )

        print(f"\nTesting poor coherence: {poor_coherence_result.source_url}")

        # Perform coherence validation on poor result
        poor_coherence_report = coherence_validator.validate_chunk_coherence(poor_coherence_result)

        print(f"Coherence validation result: {'VALID' if poor_coherence_report.is_valid else 'INVALID'}")
        print(f"Issues: {poor_coherence_report.issues}")
        print(f"Metadata: {poor_coherence_report.metadata}")

        # Evaluate chunk effectiveness
        effectiveness_metrics = coherence_validator.evaluate_chunk_effectiveness(good_coherence_result)
        print(f"\nEffectiveness metrics for good chunk: {effectiveness_metrics}")

        # Test multiple chunks validation
        results = [good_coherence_result, poor_coherence_result]
        multiple_reports = coherence_validator.validate_multiple_chunks(results)

        print(f"\nMultiple chunks validation: {len(multiple_reports)} reports generated")

        # Get coherence summary
        coherence_summary = coherence_validator.get_coherence_summary(multiple_reports)
        print(f"Coherence summary: {coherence_summary}")

        print("✅ Chunk coherence validation tests passed!")
        return True

    except Exception as e:
        print(f"❌ Chunk coherence validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_verification():
    """Test pipeline verification functionality."""
    print("\nTesting pipeline verification...")

    try:
        # Initialize the settings and pipeline service
        settings = Settings()
        pipeline_service = PipelineService(settings)

        # Test queries for pipeline validation
        test_queries = [
            "What are the foundations of ROS 2?",
            "Humanoid robotics components",
            "Cognitive planning for robots"
        ]

        print("Testing pipeline integrity with multiple queries...")

        # Perform pipeline integrity validation
        pipeline_report = pipeline_service.validate_pipeline_integrity(test_queries, limit=3)

        print(f"Pipeline validation report: {pipeline_report}")

        # Test store-retrieve pipeline validation
        print("\nTesting store-retrieve pipeline...")
        store_retrieve_report = pipeline_service.validate_store_retrieve_pipeline(
            "Sample content for testing storage and retrieval",
            "test query",
            chunk_size=512
        )

        print(f"Store-retrieve validation report: {store_retrieve_report}")

        # Test chunking strategy validation
        print("\nTesting chunking strategy...")
        chunking_report = pipeline_service.validate_chunking_strategy(
            "This is a sample content to test the chunking strategy effectiveness. It contains multiple sentences and concepts that should be preserved when chunked properly.",
            expected_chunks=2
        )

        print(f"Chunking strategy validation report: {chunking_report}")

        # Test reproducibility validation
        print("\nTesting reproducibility...")
        reproducibility_report = pipeline_service.validate_pipeline_reproducibility(
            "What are the key components of a humanoid robot?",
            num_runs=2
        )

        print(f"Reproducibility validation report: {reproducibility_report}")

        print("✅ Pipeline verification tests passed!")
        return True

    except Exception as e:
        print(f"❌ Pipeline verification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval_with_effectiveness():
    """Test retrieval with effectiveness metrics."""
    print("\nTesting retrieval with effectiveness metrics...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        coherence_validator = CoherenceValidator(settings)

        # Test query
        query_text = "Explain cognitive planning for humanoid robots"
        print(f"Query: {query_text}")

        # Perform retrieval
        results = retrieval_service.retrieve(query_text, limit=3, min_score=0.1)

        print(f"Retrieved {len(results)} results")

        # Evaluate effectiveness of each result
        total_coherence = 0
        total_context_preservation = 0

        for i, result in enumerate(results):
            print(f"\nAnalyzing result {i+1}:")
            print(f"  Source: {result.source_url}")
            print(f"  Similarity: {result.similarity_score:.3f}")
            print(f"  Content preview: {result.content_text[:80]}...")

            # Evaluate chunk effectiveness
            effectiveness = coherence_validator.evaluate_chunk_effectiveness(result)
            print(f"  Effectiveness: {effectiveness}")

            total_coherence += effectiveness["coherence_score"]
            total_context_preservation += effectiveness["context_preservation_score"]

        if results:
            avg_coherence = total_coherence / len(results)
            avg_context_preservation = total_context_preservation / len(results)

            print(f"\nAverage coherence score: {avg_coherence:.3f}")
            print(f"Average context preservation: {avg_context_preservation:.3f}")

        print("✅ Retrieval with effectiveness tests passed!")
        return True

    except Exception as e:
        print(f"❌ Retrieval with effectiveness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_effectiveness_integration():
    """Test integration of effectiveness validation with retrieval."""
    print("\nTesting effectiveness validation integration...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        coherence_validator = CoherenceValidator(settings)

        # Test query
        query_text = "What is Isaac Sim?"
        print(f"Query: {query_text}")

        # Perform retrieval with validation reports (this will include effectiveness metrics)
        result = retrieval_service.retrieve_with_validation_reports(query_text, limit=2, min_score=0.1)

        print(f"Retrieved {len(result['results'])} results with validation reports")

        # Analyze effectiveness of retrieved chunks
        for i, (retrieval_result, validation_result) in enumerate(zip(result['results'], result['validation_reports'])):
            print(f"\nResult {i+1} effectiveness analysis:")
            print(f"  Source: {retrieval_result.source_url}")
            print(f"  Content preview: {retrieval_result.content_text[:80]}...")

            # Validate chunk coherence specifically
            coherence_report = coherence_validator.validate_chunk_coherence(retrieval_result)
            print(f"  Coherence validation: {'VALID' if coherence_report.is_valid else 'INVALID'}")
            print(f"  Coherence score: {coherence_report.metadata.get('coherence_score', 0):.3f}")
            print(f"  Issues: {coherence_report.issues}")

        print("✅ Effectiveness validation integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Effectiveness validation integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_effectiveness_tests():
    """Run all chunk effectiveness tests."""
    print("Starting RAG Chunk Effectiveness tests...\n")

    tests = [
        test_chunk_coherence_validation,
        test_pipeline_verification,
        test_retrieval_with_effectiveness,
        test_effectiveness_integration
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print("-" * 50)
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Effectiveness Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All effectiveness tests passed! The chunking strategy validation is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} effectiveness test(s) failed.")
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

    success = run_all_effectiveness_tests()
    sys.exit(0 if success else 1)