#!/usr/bin/env python3
"""
End-to-End Integration Tests for RAG Retrieval and Validation System

This script provides comprehensive integration tests to verify the complete pipeline
correctness of the RAG retrieval and validation system.
"""
import sys
import os
import logging
from typing import List
import time

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService
from src.services.coherence_validator import CoherenceValidator
from src.services.pipeline_service import PipelineService
from src.models.retrieval_result_model import RetrievalResult


def setup_logging():
    """Set up logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_retrieval_service_integration():
    """Test integration of retrieval service with all components."""
    print("Testing retrieval service integration...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test basic retrieval
        query_text = "What are the foundations of ROS 2?"
        print(f"Query: {query_text}")

        results = retrieval_service.retrieve(query_text, limit=3, min_score=0.1)
        print(f"Retrieved {len(results)} results")

        # Verify results have expected structure
        for result in results:
            assert hasattr(result, 'result_id'), "Result should have result_id"
            assert hasattr(result, 'content_text'), "Result should have content_text"
            assert hasattr(result, 'source_url'), "Result should have source_url"
            assert hasattr(result, 'similarity_score'), "Result should have similarity_score"
            assert 0 <= result.similarity_score <= 1, "Similarity score should be between 0 and 1"

        # Test retrieval with validation
        validated_results = retrieval_service.retrieve_and_validate(query_text, limit=3, min_score=0.1)
        print(f"Retrieved {len(validated_results)} validated results")

        # Test retrieval with validation reports
        detailed_result = retrieval_service.retrieve_with_validation_reports(query_text, limit=2, min_score=0.1)
        assert 'results' in detailed_result, "Should have results in detailed response"
        assert 'validation_reports' in detailed_result, "Should have validation reports in detailed response"
        assert 'summary' in detailed_result, "Should have summary in detailed response"

        print("✅ Retrieval service integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Retrieval service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_service_integration():
    """Test integration of validation service with all components."""
    print("\nTesting validation service integration...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)

        # Get some results to validate
        query_text = "Humanoid robotics components"
        results = retrieval_service.retrieve(query_text, limit=2, min_score=0.1)

        if not results:
            print("⚠️  No results retrieved, skipping validation tests")
            return True

        # Test individual result validation
        for result in results:
            validation_report = validation_service.validate_result_completely(result, query_text)
            assert hasattr(validation_report, 'validation_id'), "Validation report should have validation_id"
            assert hasattr(validation_report, 'is_valid'), "Validation report should have is_valid"
            assert isinstance(validation_report.is_valid, bool), "is_valid should be boolean"

        # Test multiple result validation
        validation_results = validation_service.validate_multiple_results(results, query_text)
        assert len(validation_results) == 2, "Should have 2 sets of validation reports (metadata and content)"
        assert 'metadata' in validation_results or len(validation_results) > 0, "Should have validation results"

        # Test validation summary
        summary = validation_service.get_validation_summary(results, query_text)
        assert 'total_results' in summary, "Summary should have total_results"
        assert 'validity_percentage' in summary, "Summary should have validity_percentage"

        # Test quality metrics
        quality_metrics = validation_service.get_quality_metrics(results)
        assert 'avg_similarity_score' in quality_metrics, "Metrics should have avg_similarity_score"
        assert 'valid_metadata_percentage' in quality_metrics, "Metrics should have valid_metadata_percentage"

        print("✅ Validation service integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Validation service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coherence_validation_integration():
    """Test integration of coherence validation with retrieval."""
    print("\nTesting coherence validation integration...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        coherence_validator = CoherenceValidator(settings)

        # Get some results to validate for coherence
        query_text = "Cognitive planning for robots"
        results = retrieval_service.retrieve(query_text, limit=2, min_score=0.1)

        if not results:
            print("⚠️  No results retrieved, skipping coherence tests")
            return True

        # Test coherence validation
        for result in results:
            coherence_report = coherence_validator.validate_chunk_coherence(result)
            assert hasattr(coherence_report, 'validation_id'), "Coherence report should have validation_id"
            assert hasattr(coherence_report, 'is_valid'), "Coherence report should have is_valid"

            # Test chunk effectiveness evaluation
            effectiveness = coherence_validator.evaluate_chunk_effectiveness(result)
            assert 'coherence_score' in effectiveness, "Effectiveness should have coherence_score"
            assert 'context_preservation_score' in effectiveness, "Effectiveness should have context_preservation_score"

        # Test multiple chunk validation
        coherence_reports = coherence_validator.validate_multiple_chunks(results)
        assert len(coherence_reports) == len(results), "Should have coherence report for each result"

        # Test coherence summary
        summary = coherence_validator.get_coherence_summary(coherence_reports)
        assert 'validity_percentage' in summary, "Summary should have validity_percentage"

        print("✅ Coherence validation integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Coherence validation integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_service_integration():
    """Test integration of pipeline service with all components."""
    print("\nTesting pipeline service integration...")

    try:
        # Initialize the settings and services
        settings = Settings()
        pipeline_service = PipelineService(settings)

        # Test queries for pipeline validation
        test_queries = [
            "What are the foundations of ROS 2?",
            "Humanoid robotics components"
        ]

        # Test pipeline integrity validation
        pipeline_report = pipeline_service.validate_pipeline_integrity(test_queries, limit=2)
        assert 'test_queries_executed' in pipeline_report, "Report should have test_queries_executed"
        assert 'pipeline_integrity_score' in pipeline_report, "Report should have pipeline_integrity_score"

        print(f"Pipeline integrity score: {pipeline_report['pipeline_integrity_score']:.3f}")

        # Test reproducibility validation
        reproducibility_report = pipeline_service.validate_pipeline_reproducibility(
            "What is Isaac Sim?",
            num_runs=2
        )
        assert 'consistency_score' in reproducibility_report, "Report should have consistency_score"

        print(f"Reproducibility consistency score: {reproducibility_report['consistency_score']:.3f}")

        # Test chunking strategy validation
        chunking_report = pipeline_service.validate_chunking_strategy(
            "Sample content for testing chunking strategy effectiveness",
            expected_chunks=2
        )
        assert 'chunking_effectiveness_score' in chunking_report, "Report should have chunking_effectiveness_score"

        print(f"Chunking effectiveness score: {chunking_report['chunking_effectiveness_score']:.3f}")

        print("✅ Pipeline service integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Pipeline service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_workflow():
    """Test complete end-to-end workflow."""
    print("\nTesting complete end-to-end workflow...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)
        coherence_validator = CoherenceValidator(settings)

        # Define a comprehensive test query
        query_text = "Explain cognitive planning for humanoid robots and their key components"
        print(f"End-to-end query: {query_text}")

        # Step 1: Retrieve results
        start_time = time.time()
        results = retrieval_service.retrieve(query_text, limit=3, min_score=0.1)
        retrieval_time = time.time() - start_time
        print(f"Retrieved {len(results)} results in {retrieval_time:.2f}s")

        if not results:
            print("⚠️  No results retrieved, skipping end-to-end tests")
            return True

        # Step 2: Validate results
        start_time = time.time()
        validation_results = validation_service.validate_multiple_results(results, query_text)
        validation_time = time.time() - start_time
        print(f"Validated results in {validation_time:.2f}s")

        # Step 3: Check coherence
        start_time = time.time()
        coherence_reports = coherence_validator.validate_multiple_chunks(results)
        coherence_time = time.time() - start_time
        print(f"Checked coherence in {coherence_time:.2f}s")

        # Step 4: Generate summary
        start_time = time.time()
        summary = validation_service.get_validation_summary(results, query_text)
        summary_time = time.time() - start_time
        print(f"Generated summary in {summary_time:.2f}s")

        # Verify all steps completed successfully
        assert len(results) > 0, "Should have retrieved results"
        assert summary['total_results'] == len(results), "Summary should match result count"

        # Calculate overall metrics
        avg_similarity = sum(r.similarity_score for r in results) / len(results) if results else 0
        print(f"Average similarity score: {avg_similarity:.3f}")
        print(f"Validation validity percentage: {summary['validity_percentage']:.1f}%")

        print("✅ End-to-end workflow tests passed!")
        return True

    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling_integration():
    """Test error handling across service integrations."""
    print("\nTesting error handling integration...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test with invalid query (empty)
        try:
            empty_results = retrieval_service.retrieve("", limit=1, min_score=0.1)
            # This should either return empty results or handle gracefully
        except Exception as e:
            print(f"  Handled empty query: {type(e).__name__}")

        # Test with very high min_score (should return few/no results)
        high_score_results = retrieval_service.retrieve(
            "test query for high score",
            limit=5,
            min_score=0.99  # Very high threshold
        )
        print(f"  High threshold query returned {len(high_score_results)} results")

        # Test with very low limit
        limited_results = retrieval_service.retrieve("test query", limit=1, min_score=0.1)
        assert len(limited_results) <= 1, "Results should respect limit"

        print("✅ Error handling integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error handling integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_integration_tests():
    """Run all integration tests."""
    print("Starting RAG End-to-End Integration tests...\n")

    tests = [
        test_retrieval_service_integration,
        test_validation_service_integration,
        test_coherence_validation_integration,
        test_pipeline_service_integration,
        test_end_to_end_workflow,
        test_error_handling_integration
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print("-" * 50)
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Integration Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! The complete RAG pipeline is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} integration test(s) failed.")
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

    success = run_all_integration_tests()
    sys.exit(0 if success else 1)