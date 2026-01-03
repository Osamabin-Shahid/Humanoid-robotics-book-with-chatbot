#!/usr/bin/env python3
"""
Test Script for RAG Retrieval Validation

This script provides tests to verify the validation functionality
for the RAG retrieval and validation system, specifically focusing on
metadata alignment and content quality validation.
"""
import sys
import os
import logging
from typing import List

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService
from src.services.metadata_validator import MetadataValidator
from src.services.content_validator import ContentValidator
from src.models.retrieval_result_model import RetrievalResult


def setup_logging():
    """Set up logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_metadata_validation():
    """Test metadata validation functionality."""
    print("Testing metadata validation functionality...")

    try:
        # Initialize the settings and validation service
        settings = Settings()
        metadata_validator = MetadataValidator(settings)

        # Create a sample retrieval result with good metadata
        sample_result = RetrievalResult(
            result_id="test_result_1",
            query_text="Test query",
            content_text="This is a sample content text for testing.",
            source_url="https://example.com/test",
            similarity_score=0.85,
            chunk_id="chunk_123",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://example.com/test",
                "chunk_id": "chunk_123",
                "content": "This is a sample content text for testing.",
                "created_at": "2025-12-27T10:00:00Z"
            }
        )

        print(f"Testing valid result: {sample_result.source_url}")

        # Perform validation
        validation_report = metadata_validator.validate_metadata_alignment(sample_result)

        print(f"Validation result: {'VALID' if validation_report.is_valid else 'INVALID'}")
        print(f"Issues: {validation_report.issues}")
        print(f"Metadata: {validation_report.metadata}")

        # Create a sample retrieval result with bad metadata
        bad_result = RetrievalResult(
            result_id="test_result_2",
            query_text="Test query",
            content_text="",
            source_url="invalid-url",
            similarity_score=1.5,  # Invalid score
            chunk_id="",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://different.com/test",  # Mismatch with result
                "chunk_id": "different_chunk",  # Mismatch with result
                "content": "Different content",  # Mismatch with result
            }
        )

        print(f"\nTesting invalid result: {bad_result.source_url}")

        # Perform validation on bad result
        bad_validation_report = metadata_validator.validate_metadata_alignment(bad_result)

        print(f"Validation result: {'VALID' if bad_validation_report.is_valid else 'INVALID'}")
        print(f"Issues: {bad_validation_report.issues}")
        print(f"Metadata: {bad_validation_report.metadata}")

        # Test multiple results validation
        results = [sample_result, bad_result]
        multiple_reports = metadata_validator.validate_multiple_results(results)

        print(f"\nMultiple results validation: {len(multiple_reports)} reports generated")

        # Get summary
        summary = metadata_validator.get_validation_summary(multiple_reports)
        print(f"Summary: {summary}")

        print("✅ Metadata validation tests passed!")
        return True

    except Exception as e:
        print(f"❌ Metadata validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_content_validation():
    """Test content validation functionality."""
    print("\nTesting content validation functionality...")

    try:
        # Initialize the settings and validation service
        settings = Settings()
        content_validator = ContentValidator(settings)

        # Create a sample retrieval result with good content
        good_result = RetrievalResult(
            result_id="test_result_3",
            query_text="Test query about robotics",
            content_text="Humanoid robotics is an interdisciplinary branch of robotics that studies and develops robots with human-like features, allowing them to interact with human tools and environments.",
            source_url="https://example.com/robotics",
            similarity_score=0.82,
            chunk_id="chunk_456",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://example.com/robotics",
                "chunk_id": "chunk_456",
                "content": "Humanoid robotics is an interdisciplinary branch of robotics that studies and develops robots with human-like features, allowing them to interact with human tools and environments.",
                "created_at": "2025-12-27T10:00:00Z"
            }
        )

        print(f"Testing good content: {good_result.source_url}")

        # Perform content validation
        content_validation_report = content_validator.validate_content_quality(good_result, "robotics")

        print(f"Content validation result: {'VALID' if content_validation_report.is_valid else 'INVALID'}")
        print(f"Issues: {content_validation_report.issues}")
        print(f"Metadata: {content_validation_report.metadata}")

        # Create a sample retrieval result with poor content
        poor_result = RetrievalResult(
            result_id="test_result_4",
            query_text="Test query",
            content_text="This is very short. AAAAAAAAAAAAAAAAAAAAAA This has excessive repetition.",
            source_url="https://example.com/poor",
            similarity_score=0.3,
            chunk_id="chunk_789",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://example.com/poor",
                "chunk_id": "chunk_789",
                "content": "This is very short. AAAAAAAAAAAAAAAAAAAAAA This has excessive repetition.",
                "created_at": "2025-12-27T10:00:00Z"
            }
        )

        print(f"\nTesting poor content: {poor_result.source_url}")

        # Perform content validation on poor result
        poor_content_validation = content_validator.validate_content_quality(poor_result, "general topic")

        print(f"Content validation result: {'VALID' if poor_content_validation.is_valid else 'INVALID'}")
        print(f"Issues: {poor_content_validation.issues}")
        print(f"Metadata: {poor_content_validation.metadata}")

        # Test multiple results validation
        results = [good_result, poor_result]
        multiple_content_reports = content_validator.validate_multiple_results(results, "robotics")

        print(f"\nMultiple content validation: {len(multiple_content_reports)} reports generated")

        # Get content quality summary
        content_summary = content_validator.get_content_quality_summary(multiple_content_reports)
        print(f"Content quality summary: {content_summary}")

        print("✅ Content validation tests passed!")
        return True

    except Exception as e:
        print(f"❌ Content validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_validation():
    """Test comprehensive validation combining metadata and content validation."""
    print("\nTesting comprehensive validation functionality...")

    try:
        # Initialize the settings and validation service
        settings = Settings()
        validation_service = ValidationService(settings)

        # Create a sample retrieval result
        sample_result = RetrievalResult(
            result_id="test_result_5",
            query_text="What are the foundations of ROS 2?",
            content_text="ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.",
            source_url="https://docs.ros.org/en/rolling/index.html",
            similarity_score=0.78,
            chunk_id="ros2_foundation_001",
            created_at="2025-12-27T10:00:00Z",
            metadata={
                "source_url": "https://docs.ros.org/en/rolling/index.html",
                "chunk_id": "ros2_foundation_001",
                "content": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.",
                "created_at": "2025-12-27T10:00:00Z",
                "document_type": "documentation",
                "section": "introduction"
            }
        )

        print(f"Testing comprehensive validation: {sample_result.source_url}")

        # Perform comprehensive validation
        comprehensive_report = validation_service.validate_result_completely(sample_result, "ROS 2 foundations")

        print(f"Comprehensive validation result: {'VALID' if comprehensive_report.is_valid else 'INVALID'}")
        print(f"Issues: {comprehensive_report.issues}")
        print(f"Metadata: {comprehensive_report.metadata}")

        # Test multiple results comprehensive validation
        results = [sample_result]
        multiple_validation_results = validation_service.validate_multiple_results(results, "ROS 2 foundations")

        print(f"\nMultiple comprehensive validation:")
        print(f"  Metadata reports: {len(multiple_validation_results['metadata'])}")
        print(f"  Content reports: {len(multiple_validation_results['content'])}")

        # Get comprehensive summary
        comprehensive_summary = validation_service.get_validation_summary(results, "ROS 2 foundations")
        print(f"\nComprehensive summary: {comprehensive_summary}")

        # Get quality metrics
        quality_metrics = validation_service.get_quality_metrics(results)
        print(f"Quality metrics: {quality_metrics}")

        print("✅ Comprehensive validation tests passed!")
        return True

    except Exception as e:
        print(f"❌ Comprehensive validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_integration_with_retrieval():
    """Test validation integrated with retrieval service."""
    print("\nTesting validation integration with retrieval service...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test query
        query_text = "What are the key components of humanoid robotics?"
        print(f"Query: {query_text}")

        # Perform retrieval with validation reports
        result = retrieval_service.retrieve_with_validation_reports(query_text, limit=2, min_score=0.1)

        print(f"Retrieved {len(result['results'])} results")
        print(f"Generated {len(result['validation_reports'])} validation reports")
        print(f"Summary: {result['summary']}")

        # Perform quality validation
        expected_keywords = ["robot", "components", "humanoid", "actuator", "sensor"]
        quality_result = retrieval_service.validate_retrieval_quality(
            query_text, expected_keywords, limit=2
        )

        print(f"Quality validation result: {quality_result}")

        print("✅ Validation integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Validation integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_validation_tests():
    """Run all validation tests."""
    print("Starting RAG Retrieval Validation tests...\n")

    tests = [
        test_metadata_validation,
        test_content_validation,
        test_comprehensive_validation,
        test_validation_integration_with_retrieval
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print("-" * 50)
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Validation Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All validation tests passed! The RAG validation system is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} validation test(s) failed.")
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

    success = run_all_validation_tests()
    sys.exit(0 if success else 1)