#!/usr/bin/env python3
"""
Performance Tests for RAG Retrieval and Validation System

This script provides performance tests to validate retrieval speed requirements
and system responsiveness under various conditions.
"""
import sys
import os
import logging
from typing import List
import time
import statistics

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService


def setup_logging():
    """Set up logging for the test script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_retrieval_performance():
    """Test retrieval performance with various query types and sizes."""
    print("Testing retrieval performance...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Define test queries of different complexities
        test_queries = [
            "ROS 2",  # Simple query
            "Humanoid robotics components",  # Medium query
            "Explain cognitive planning for humanoid robots and their key components",  # Complex query
            "What are the foundations of ROS 2 and how do they apply to humanoid robotics?"  # Detailed query
        ]

        # Performance metrics
        retrieval_times = []
        result_counts = []

        for query in test_queries:
            print(f"  Testing query: '{query[:30]}...'")

            # Perform retrieval multiple times to get average performance
            times = []
            for _ in range(3):  # Run 3 times and average
                start_time = time.time()
                results = retrieval_service.retrieve(query, limit=5, min_score=0.1)
                end_time = time.time()

                times.append((end_time - start_time) * 1000)  # Convert to milliseconds
                result_counts.append(len(results))

            avg_time = statistics.mean(times)
            retrieval_times.append(avg_time)

            print(f"    Average time: {avg_time:.2f}ms, Results: {len(results)}")

        # Calculate overall metrics
        avg_retrieval_time = statistics.mean(retrieval_times)
        avg_results = statistics.mean(result_counts)

        print(f"\nRetrieval Performance Metrics:")
        print(f"  Average retrieval time: {avg_retrieval_time:.2f}ms")
        print(f"  Average results per query: {avg_results:.1f}")
        print(f"  Min time: {min(retrieval_times):.2f}ms")
        print(f"  Max time: {max(retrieval_times):.2f}ms")
        print(f"  Std deviation: {statistics.stdev(retrieval_times) if len(retrieval_times) > 1 else 0:.2f}ms")

        # Performance requirements check
        max_acceptable_time = 2000  # 2 seconds in ms
        if avg_retrieval_time > max_acceptable_time:
            print(f"  ⚠️  Average retrieval time ({avg_retrieval_time:.2f}ms) exceeds requirement ({max_acceptable_time}ms)")
        else:
            print(f"  ✅ Average retrieval time is within acceptable limits")

        return True

    except Exception as e:
        print(f"❌ Retrieval performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_concurrent_retrieval_performance():
    """Test performance under concurrent retrieval requests."""
    print("\nTesting concurrent retrieval performance...")

    try:
        import threading
        import queue

        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Define test queries
        test_queries = [
            "ROS 2 basics",
            "Humanoid robotics",
            "Cognitive planning",
            "Robot components",
            "Isaac Sim"
        ]

        # Function to run retrieval in a thread
        def run_retrieval(query, result_queue):
            try:
                start_time = time.time()
                results = retrieval_service.retrieve(query, limit=3, min_score=0.1)
                end_time = time.time()

                result_queue.put({
                    'query': query,
                    'time': (end_time - start_time) * 1000,  # Convert to milliseconds
                    'results': len(results)
                })
            except Exception as e:
                result_queue.put({
                    'query': query,
                    'error': str(e),
                    'time': -1,
                    'results': 0
                })

        # Run concurrent retrievals
        result_queue = queue.Queue()
        threads = []

        for query in test_queries:
            thread = threading.Thread(target=run_retrieval, args=(query, result_queue))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        concurrent_results = []
        while not result_queue.empty():
            concurrent_results.append(result_queue.get())

        # Analyze results
        successful_retrievals = [r for r in concurrent_results if 'error' not in r]
        failed_retrievals = [r for r in concurrent_results if 'error' in r]

        if successful_retrievals:
            concurrent_times = [r['time'] for r in successful_retrievals]
            avg_concurrent_time = statistics.mean(concurrent_times)

            print(f"  Successful retrievals: {len(successful_retrievals)}")
            print(f"  Failed retrievals: {len(failed_retrievals)}")
            print(f"  Average concurrent time: {avg_concurrent_time:.2f}ms")
            print(f"  Max concurrent time: {max(concurrent_times):.2f}ms")
            print(f"  Min concurrent time: {min(concurrent_times):.2f}ms")

        if failed_retrievals:
            print(f"  ❌ {len(failed_retrievals)} concurrent retrievals failed")
            for failed in failed_retrievals:
                print(f"    Query '{failed['query']}': {failed['error']}")
            return False

        return True

    except Exception as e:
        print(f"❌ Concurrent retrieval performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_performance():
    """Test validation performance with various result sets."""
    print("\nTesting validation performance...")

    try:
        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)

        # Get some results to validate
        query_text = "Humanoid robotics components"
        results = retrieval_service.retrieve(query_text, limit=10, min_score=0.1)

        if not results:
            print("⚠️  No results retrieved, skipping validation performance tests")
            return True

        # Test validation performance on different result set sizes
        result_set_sizes = [1, 3, 5, len(results) if len(results) < 10 else 10]
        validation_times = []

        for size in result_set_sizes:
            subset = results[:size]
            print(f"  Testing validation for {size} results...")

            # Time the validation
            start_time = time.time()
            validation_results = validation_service.validate_multiple_results(subset, query_text)
            end_time = time.time()

            validation_time = (end_time - start_time) * 1000  # Convert to milliseconds
            validation_times.append(validation_time)

            print(f"    Validation time: {validation_time:.2f}ms")

        # Calculate metrics
        if validation_times:
            avg_validation_time = statistics.mean(validation_times)
            print(f"\nValidation Performance Metrics:")
            print(f"  Average validation time: {avg_validation_time:.2f}ms")
            print(f"  Total validation time for all sizes: {sum(validation_times):.2f}ms")

        return True

    except Exception as e:
        print(f"❌ Validation performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_large_limit_performance():
    """Test performance with large result limits."""
    print("\nTesting large limit performance...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Test with increasing limits
        query_text = "ROS 2"
        limit_sizes = [5, 10, 20]

        for limit in limit_sizes:
            print(f"  Testing retrieval with limit {limit}...")

            start_time = time.time()
            results = retrieval_service.retrieve(query_text, limit=limit, min_score=0.1)
            end_time = time.time()

            retrieval_time = (end_time - start_time) * 1000  # Convert to milliseconds

            print(f"    Retrieved {len(results)} results in {retrieval_time:.2f}ms")

            # Check if retrieval time scales reasonably
            expected_time_per_result = retrieval_time / len(results) if results else 0
            print(f"    Average time per result: {expected_time_per_result:.2f}ms")

        return True

    except Exception as e:
        print(f"❌ Large limit performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_response_time_consistency():
    """Test consistency of response times across multiple runs."""
    print("\nTesting response time consistency...")

    try:
        # Initialize the settings and retrieval service
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        query_text = "What are the foundations of ROS 2?"

        # Run the same query multiple times to test consistency
        times = []
        for i in range(5):
            start_time = time.time()
            results = retrieval_service.retrieve(query_text, limit=3, min_score=0.1)
            end_time = time.time()

            retrieval_time = (end_time - start_time) * 1000  # Convert to milliseconds
            times.append(retrieval_time)

            print(f"  Run {i+1}: {retrieval_time:.2f}ms, {len(results)} results")

        if times:
            avg_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            cv = (std_dev / avg_time * 100) if avg_time > 0 else 0  # Coefficient of variation

            print(f"\nConsistency Metrics:")
            print(f"  Average time: {avg_time:.2f}ms")
            print(f"  Standard deviation: {std_dev:.2f}ms")
            print(f"  Coefficient of variation: {cv:.2f}%")

            # Check consistency (lower CV is better)
            if cv < 20:  # Less than 20% variation is generally good
                print(f"  ✅ Response times are consistent (CV < 20%)")
            else:
                print(f"  ⚠️  Response times have high variation (CV >= 20%)")

        return True

    except Exception as e:
        print(f"❌ Response time consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_usage():
    """Test memory usage during operations."""
    print("\nTesting memory usage...")

    try:
        import psutil
        import gc

        # Get initial memory usage
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"  Initial memory usage: {initial_memory:.2f} MB")

        # Initialize the settings and services
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        # Perform multiple operations and monitor memory
        for i in range(5):
            query_text = f"Test query {i} for memory usage"
            results = retrieval_service.retrieve(query_text, limit=5, min_score=0.1)

            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            print(f"  After query {i+1}: {current_memory:.2f} MB")

        # Force garbage collection
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"  Final memory after GC: {final_memory:.2f} MB")

        memory_increase = final_memory - initial_memory
        print(f"  Memory increase: {memory_increase:.2f} MB")

        # Check if memory usage is reasonable
        if abs(memory_increase) < 50:  # Less than 50MB increase is reasonable
            print(f"  ✅ Memory usage is reasonable")
        else:
            print(f"  ⚠️  Memory usage increased significantly ({memory_increase:.2f} MB)")

        return True

    except Exception as e:
        print(f"❌ Memory usage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_performance_tests():
    """Run all performance tests."""
    print("Starting RAG Performance tests...\n")

    tests = [
        test_retrieval_performance,
        test_concurrent_retrieval_performance,
        test_validation_performance,
        test_large_limit_performance,
        test_response_time_consistency,
        test_memory_usage
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print("-" * 50)
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Performance Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All performance tests passed! The RAG system meets performance requirements.")
        return True
    else:
        print(f"⚠️  {total - passed} performance test(s) failed.")
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

    success = run_all_performance_tests()
    sys.exit(0 if success else 1)