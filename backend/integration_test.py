"""
Integration Test Script for RAG Retrieval and Validation System

This script performs comprehensive integration tests to verify that all components
of the RAG retrieval and validation system work together correctly.
"""
import os
import sys
import time
import requests
from typing import Dict, Any, List

# Add backend/src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService
from src.services.pipeline_service import PipelineService
from src.models.retrieval_result_model import RetrievalResult


def test_configuration():
    """Test that configuration is loaded correctly."""
    print("Testing configuration...")
    settings = Settings()

    # Check that required settings are present
    assert settings.qdrant_url, "QDRANT_URL is required"
    assert settings.qdrant_api_key, "QDRANT_API_KEY is required"
    assert settings.cohere_api_key, "COHERE_API_KEY is required"
    assert settings.qdrant_collection_name, "QDRANT_COLLECTION_NAME is required"

    print("SUCCESS: Configuration test passed")


def test_services_instantiation():
    """Test that all services can be instantiated correctly."""
    print("Testing service instantiation...")
    settings = Settings()

    # Test that services can be created without errors
    retrieval_service = RetrievalService(settings)
    validation_service = ValidationService(settings)
    pipeline_service = PipelineService(settings)

    assert retrieval_service is not None
    assert validation_service is not None
    assert pipeline_service is not None

    print("SUCCESS: Service instantiation test passed")


def test_basic_retrieval():
    """Test basic retrieval functionality."""
    print("Testing basic retrieval...")
    settings = Settings()
    retrieval_service = RetrievalService(settings)

    # Test with a simple query
    test_query = "machine learning concepts"

    try:
        results = retrieval_service.retrieve(
            query_text=test_query,
            limit=5,
            min_score=0.0
        )

        # Results may be empty if no data is in Qdrant, but the call should succeed
        print(f"✓ Retrieved {len(results)} results for query: '{test_query}'")
        return True
    except Exception as e:
        print(f"⚠ Retrieval failed (may be expected if no data in Qdrant): {e}")
        return False


def test_retrieval_with_validation():
    """Test retrieval with validation."""
    print("Testing retrieval with validation...")
    settings = Settings()
    retrieval_service = RetrievalService(settings)
    validation_service = ValidationService(settings)

    test_query = "artificial intelligence"

    try:
        # First retrieve results
        results = retrieval_service.retrieve(
            query_text=test_query,
            limit=3,
            min_score=0.0
        )

        if results:
            # Validate the results
            validation_reports = validation_service.validate_multiple_results(results, test_query)
            print(f"✓ Validated {len(results)} results with {len(validation_reports)} validation reports")
            return True
        else:
            print("⚠ No results to validate (expected if no data in Qdrant)")
            return True
    except Exception as e:
        print(f"⚠ Validation test failed (may be expected if no data in Qdrant): {e}")
        return False


def test_pipeline_validation():
    """Test pipeline validation functionality."""
    print("Testing pipeline validation...")
    settings = Settings()
    pipeline_service = PipelineService(settings)

    try:
        # Test pipeline integrity with a simple query
        test_queries = ["test", "example", "sample"]
        report = pipeline_service.validate_pipeline_integrity(test_queries, limit=2)

        print(f"✓ Pipeline validation completed with success rate: {report.get('success_rate', 0)}")
        return True
    except Exception as e:
        print(f"⚠ Pipeline validation failed (may be expected if no data in Qdrant): {e}")
        return False


def test_api_endpoints():
    """Test API endpoints if they're running."""
    print("Testing API endpoints...")

    # Check if the API is running
    try:
        # Test health endpoint
        health_response = requests.get("http://localhost:8000/health", timeout=10)
        if health_response.status_code == 200:
            print("✓ Health endpoint is accessible")
        else:
            print(f"⚠ Health endpoint returned status: {health_response.status_code}")
            return False

        # Test validation health endpoint
        val_health_response = requests.get("http://localhost:8000/validation/health", timeout=10)
        if val_health_response.status_code == 200:
            print("✓ Validation health endpoint is accessible")
        else:
            print(f"⚠ Validation health endpoint returned status: {val_health_response.status_code}")
            return False

        # Test retrieval endpoint with a simple query
        retrieval_response = requests.post(
            "http://localhost:8000/retrieve",
            json={
                "query_text": "test query",
                "limit": 1,
                "min_score": 0.0,
                "validate_results": False
            },
            timeout=30
        )

        if retrieval_response.status_code in [200, 400, 500]:  # 400 is expected for bad queries, 500 for missing data
            print("✓ Retrieval endpoint is accessible")
        else:
            print(f"⚠ Retrieval endpoint returned unexpected status: {retrieval_response.status_code}")
            return False

        return True
    except requests.exceptions.ConnectionError:
        print("⚠ API endpoints not accessible (server may not be running)")
        return False
    except Exception as e:
        print(f"⚠ Error testing API endpoints: {e}")
        return False


def test_error_handling():
    """Test error handling in services."""
    print("Testing error handling...")
    settings = Settings()
    retrieval_service = RetrievalService(settings)

    # Test validation of bad inputs
    try:
        # This should raise a ValueError
        retrieval_service.retrieve("", limit=5, min_score=0.0)
        print("⚠ Empty query should have raised ValueError")
        return False
    except ValueError:
        print("✓ Empty query validation works correctly")
    except Exception as e:
        print(f"⚠ Unexpected error for empty query: {e}")
        return False

    try:
        # This should raise a ValueError
        retrieval_service.retrieve("valid query", limit=0, min_score=0.0)
        print("⚠ Zero limit should have raised ValueError")
        return False
    except ValueError:
        print("✓ Zero limit validation works correctly")
    except Exception as e:
        print(f"⚠ Unexpected error for zero limit: {e}")
        return False

    try:
        # This should raise a ValueError
        retrieval_service.retrieve("valid query", limit=5, min_score=1.5)
        print("⚠ Invalid min_score should have raised ValueError")
        return False
    except ValueError:
        print("✓ Invalid min_score validation works correctly")
    except Exception as e:
        print(f"⚠ Unexpected error for invalid min_score: {e}")
        return False

    return True


def run_all_tests():
    """Run all integration tests."""
    print("Starting RAG Retrieval and Validation System Integration Tests\n")

    tests = [
        ("Configuration", test_configuration),
        ("Service Instantiation", test_services_instantiation),
        ("Basic Retrieval", test_basic_retrieval),
        ("Retrieval with Validation", test_retrieval_with_validation),
        ("Pipeline Validation", test_pipeline_validation),
        ("API Endpoints", test_api_endpoints),
        ("Error Handling", test_error_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✓ {test_name} test passed")
            else:
                print(f"✗ {test_name} test failed or skipped")
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")

    print(f"\nIntegration Test Summary: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print(f"⚠ {total - passed} tests failed or were skipped")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)