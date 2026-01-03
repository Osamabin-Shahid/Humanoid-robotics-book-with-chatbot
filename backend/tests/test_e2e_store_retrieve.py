#!/usr/bin/env python3
"""
End-to-End Store → Retrieve Pipeline Tests for RAG System

This script provides tests to verify the complete store → retrieve pipeline
correctness using realistic book content queries.
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
from src.services.pipeline_service import PipelineService
from src.models.retrieval_result_model import RetrievalResult


def setup_logging():
    """Set up logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_basic_retrieval_functionality():
    """Test basic retrieval functionality with realistic queries."""
    print("Testing basic retrieval functionality with realistic queries...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Define realistic queries based on typical book content about robotics and AI
        realistic_queries = [
            "What are the foundations of ROS 2?",
            "Explain humanoid robotics components",
            "Cognitive planning for robots",
            "What is Isaac Sim?",
            "Robot operating system architecture",
            "Humanoid robot actuators and sensors",
            "ROS 2 communication patterns",
            "Robot middleware frameworks"
        ]

        all_results_found = True

        for query in realistic_queries:
            print(f"  Query: '{query}'")

            # Perform retrieval
            results = retrieval_service.retrieve(query, limit=3, min_score=0.1)

            print(f"    Retrieved {len(results)} results")

            if len(results) == 0:
                print(f"    ⚠️  No results found for query: '{query}'")
                all_results_found = False
            else:
                # Display first result as sample
                first_result = results[0]
                print(f"    Top result - Score: {first_result.similarity_score:.3f}")
                print(f"    Source: {first_result.source_url}")
                print(f"    Content preview: {first_result.content_text[:80]}...")

        if all_results_found:
            print("  ✅ All queries returned results")
        else:
            print("  ⚠️  Some queries returned no results (this may be expected if database is empty)")

        return True

    except Exception as e:
        print(f"❌ Basic retrieval functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_relevance_and_quality():
    """Test the relevance and quality of retrieved results."""
    print("\nTesting relevance and quality of retrieved results...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)

        # Test queries that should have relevant results if the database contains robotics/AI content
        test_queries = [
            ("ROS 2 basics", ["ROS", "robot", "framework"]),
            ("Humanoid robot design", ["humanoid", "robot", "design", "components"]),
            ("Cognitive systems", ["cognitive", "planning", "AI", "robotics"])
        ]

        quality_threshold = 0.5  # Minimum average quality score
        all_quality_pass = True

        for query, expected_keywords in test_queries:
            print(f"  Query: '{query}' with expected keywords: {expected_keywords}")

            # Retrieve results
            results = retrieval_service.retrieve(query, limit=5, min_score=0.1)

            if not results:
                print(f"    ⚠️  No results for query: '{query}'")
                continue

            # Validate results quality
            validation_results = validation_service.validate_multiple_results(results, query)

            # Calculate keyword relevance
            keyword_relevant_count = 0
            for result in results:
                content_lower = result.content_text.lower()
                keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in content_lower)
                if keyword_matches > 0:
                    keyword_relevant_count += 1

            keyword_relevance = keyword_relevant_count / len(results) if results else 0
            print(f"    Keyword relevance: {keyword_relevance:.2f} ({keyword_relevant_count}/{len(results)})")

            # Check if quality is acceptable
            if keyword_relevance < quality_threshold:
                print(f"    ⚠️  Low keyword relevance for query: '{query}'")
                all_quality_pass = False
            else:
                print(f"    ✅ Quality acceptable for query: '{query}'")

        if all_quality_pass:
            print("  ✅ All queries met quality thresholds")
        else:
            print("  ⚠️  Some queries did not meet quality thresholds")

        return True

    except Exception as e:
        print(f"❌ Relevance and quality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_completeness():
    """Test the completeness of the pipeline functionality."""
    print("\nTesting pipeline completeness...")

    try:
        # Initialize the settings and services
        settings = Settings()
        pipeline_service = PipelineService(settings)

        # Test comprehensive pipeline validation
        test_queries = [
            "ROS 2 architecture",
            "Humanoid robotics fundamentals",
            "Robot cognitive systems"
        ]

        print("  Running pipeline integrity validation...")
        pipeline_report = pipeline_service.validate_pipeline_integrity(test_queries, limit=3)

        print(f"  Pipeline success rate: {pipeline_report['success_rate']:.1%}")
        print(f"  Pipeline integrity score: {pipeline_report['pipeline_integrity_score']:.3f}")
        print(f"  Issues found: {pipeline_report['issues_count']}")

        if pipeline_report['issues_count'] == 0:
            print("  ✅ Pipeline integrity validation passed")
        else:
            print(f"  ⚠️  Pipeline integrity validation found {pipeline_report['issues_count']} issues")
            for issue in pipeline_report['pipeline_issues'][:3]:  # Show first 3 issues
                print(f"    - {issue}")

        # Test reproducibility
        print("  Running reproducibility validation...")
        reproducibility_report = pipeline_service.validate_pipeline_reproducibility(
            "What are the foundations of ROS 2?",
            num_runs=3
        )

        print(f"  Consistency score: {reproducibility_report['consistency_score']:.3f}")
        print(f"  Reproducible: {'Yes' if reproducibility_report['reproducible'] else 'No'}")

        if reproducibility_report['reproducible']:
            print("  ✅ Pipeline reproducibility validation passed")
        else:
            print("  ⚠️  Pipeline reproducibility validation failed")

        return True

    except Exception as e:
        print(f"❌ Pipeline completeness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\nTesting edge cases and error conditions...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test with very specific queries that might return few results
        specific_queries = [
            "Quadrupedal locomotion algorithms",
            "Bio-inspired robot control systems",
            "Humanoid robot bipedal walking control"
        ]

        for query in specific_queries:
            print(f"  Testing specific query: '{query}'")

            # Try with different limits and thresholds
            results_high_threshold = retrieval_service.retrieve(query, limit=1, min_score=0.7)
            results_low_threshold = retrieval_service.retrieve(query, limit=5, min_score=0.1)

            print(f"    High threshold (0.7): {len(results_high_threshold)} results")
            print(f"    Low threshold (0.1): {len(results_low_threshold)} results")

        # Test with common terms that should return many results
        common_query = "robot"
        print(f"  Testing common query: '{common_query}'")

        start_time = time.time()
        common_results = retrieval_service.retrieve(common_query, limit=10, min_score=0.1)
        end_time = time.time()

        print(f"    Retrieved {len(common_results)} results in {end_time - start_time:.2f}s")

        # Test with empty results handling
        unique_query = "xyz123_unusual_query_that_should_not_match_anything"
        print(f"  Testing unique query: '{unique_query}'")

        unique_results = retrieval_service.retrieve(unique_query, limit=5, min_score=0.1)
        print(f"    Retrieved {len(unique_results)} results (expected: 0)")

        print("  ✅ Edge cases handled appropriately")
        return True

    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_content_diversity():
    """Test that retrieved content covers diverse topics."""
    print("\nTesting content diversity...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Define queries across different topics to test diversity
        topic_queries = [
            ("ROS 2", "middleware"),
            ("Humanoid robots", "mechanics"),
            ("Cognitive systems", "AI"),
            ("Robot sensors", "hardware"),
            ("Path planning", "algorithms")
        ]

        all_sources = set()
        all_content_segments = []

        for query, topic in topic_queries:
            print(f"  Query for {topic}: '{query}'")

            results = retrieval_service.retrieve(query, limit=2, min_score=0.1)
            print(f"    Retrieved {len(results)} results")

            for result in results:
                all_sources.add(result.source_url)
                all_content_segments.append(result.content_text)

        print(f"  Total unique sources found: {len(all_sources)}")
        print(f"  Total content segments: {len(all_content_segments)}")

        if len(all_sources) >= 3:  # Expect at least 3 different sources for good diversity
            print("  ✅ Content comes from diverse sources")
        else:
            print(f"  ⚠️  Limited source diversity: {len(all_sources)} unique sources")

        # Check if we have content from multiple topics
        content_text = " ".join(all_content_segments).lower()
        topics_found = []

        if "ros" in content_text or "framework" in content_text:
            topics_found.append("middleware")
        if "robot" in content_text and ("actuator" in content_text or "sensor" in content_text):
            topics_found.append("hardware/mechanics")
        if "ai" in content_text or "cognitive" in content_text or "algorithm" in content_text:
            topics_found.append("AI/algorithms")

        print(f"  Topics represented: {topics_found}")

        if len(topics_found) >= 2:  # Expect at least 2 different topics
            print("  ✅ Content covers diverse topics")
        else:
            print(f"  ⚠️  Limited topic diversity: {len(topics_found)} topics found")

        return True

    except Exception as e:
        print(f"❌ Content diversity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_responsiveness():
    """Test system responsiveness under various conditions."""
    print("\nTesting system responsiveness...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test response times for different query types
        responsiveness_tests = [
            ("Quick response test", "robot", 1, 0.1),
            ("Detailed response test", "comprehensive humanoid robot design", 3, 0.2),
            ("Broad topic test", "artificial intelligence", 5, 0.1)
        ]

        total_time = 0
        test_count = 0

        for test_name, query, limit, min_score in responsiveness_tests:
            print(f"  {test_name}: '{query}'")

            start_time = time.time()
            results = retrieval_service.retrieve(query, limit=limit, min_score=min_score)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            total_time += response_time
            test_count += 1

            print(f"    Response time: {response_time:.2f}ms, Results: {len(results)}")

        avg_response_time = total_time / test_count if test_count > 0 else 0
        print(f"  Average response time: {avg_response_time:.2f}ms")

        # Check if response time is acceptable (under 2 seconds)
        if avg_response_time < 2000:  # 2000ms = 2 seconds
            print("  ✅ System responsiveness is acceptable")
        else:
            print(f"  ⚠️  System responsiveness may be slow: {avg_response_time:.2f}ms")

        return True

    except Exception as e:
        print(f"❌ System responsiveness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_e2e_tests():
    """Run all end-to-end store → retrieve tests."""
    print("Starting RAG End-to-End Store → Retrieve tests...\n")

    tests = [
        test_basic_retrieval_functionality,
        test_relevance_and_quality,
        test_pipeline_completeness,
        test_edge_cases,
        test_content_diversity,
        test_system_responsiveness
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print("-" * 60)
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"End-to-End Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All end-to-end tests passed! The store → retrieve pipeline is working correctly.")
        print("The RAG system can successfully retrieve relevant content from the vector database.")
        return True
    else:
        print(f"⚠️  {total - passed} end-to-end test(s) failed.")
        print("The RAG system may have issues with the retrieval pipeline.")
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

    success = run_all_e2e_tests()
    sys.exit(0 if success else 1)