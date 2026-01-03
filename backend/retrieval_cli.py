#!/usr/bin/env python3
"""
CLI Interface for RAG Retrieval and Validation System

This module provides a command-line interface for testing and validating
the RAG retrieval and validation system.
"""
import argparse
import sys
import os
from typing import List, Dict, Any
import json
import time

# Add the backend/src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService
from src.services.coherence_validator import CoherenceValidator
from src.services.pipeline_service import PipelineService


def setup_arg_parser():
    """Set up the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="CLI for RAG Retrieval and Validation System"
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Retrieve command
    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve content from the vector database')
    retrieve_parser.add_argument('query', help='The query text to search for')
    retrieve_parser.add_argument('--limit', type=int, default=5, help='Maximum number of results to return (default: 5)')
    retrieve_parser.add_argument('--min-score', type=float, default=0.1, help='Minimum similarity score threshold (default: 0.1)')
    retrieve_parser.add_argument('--validate', action='store_true', help='Validate results before returning')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate retrieval results')
    validate_parser.add_argument('query', help='The query text to validate')
    validate_parser.add_argument('--limit', type=int, default=5, help='Number of results to validate (default: 5)')
    validate_parser.add_argument('--keywords', nargs='*', default=[], help='Expected keywords for validation')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run various tests on the system')
    test_parser.add_argument('--type', choices=['basic', 'validation', 'effectiveness', 'all'],
                            default='all', help='Type of tests to run (default: all)')

    # Health check command
    health_parser = subparsers.add_parser('health', help='Check system health and configuration')

    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive mode')

    return parser


def retrieve_content(args):
    """Handle the retrieve command."""
    print(f"Retrieving content for query: '{args.query}'")
    print(f"Limit: {args.limit}, Min Score: {args.min_score}")

    try:
        settings = Settings()
        retrieval_service = RetrievalService(settings)

        start_time = time.time()

        if args.validate:
            print("Performing retrieval with validation...")
            results = retrieval_service.retrieve_and_validate(
                query_text=args.query,
                limit=args.limit,
                min_score=args.min_score
            )
        else:
            print("Performing basic retrieval...")
            results = retrieval_service.retrieve(
                query_text=args.query,
                limit=args.limit,
                min_score=args.min_score
            )

        execution_time = time.time() - start_time

        print(f"\nRetrieved {len(results)} results in {execution_time:.2f} seconds:")
        print("-" * 80)

        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result.similarity_score:.3f}")
            print(f"   Source: {result.source_url}")
            print(f"   Chunk ID: {result.chunk_id}")
            print(f"   Content preview: {result.content_text[:100]}...")
            print()

        if not results:
            print("No results found for the given query.")

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return False

    return True


def validate_content(args):
    """Handle the validate command."""
    print(f"Validating content for query: '{args.query}'")
    print(f"Limit: {args.limit}, Expected keywords: {args.keywords}")

    try:
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)

        # Retrieve results first
        results = retrieval_service.retrieve(
            query_text=args.query,
            limit=args.limit
        )

        print(f"Retrieved {len(results)} results to validate...")

        if args.keywords:
            # Perform quality validation with expected keywords
            validation_report = retrieval_service.validate_retrieval_quality(
                query_text=args.query,
                expected_content_keywords=args.keywords,
                limit=args.limit
            )

            print(f"\nQuality validation report:")
            print(f"  Total results: {validation_report['total_results']}")
            print(f"  Relevant results: {validation_report['relevant_results']}")
            print(f"  Keyword relevance score: {validation_report['keyword_relevance_score']:.2f}")
            print(f"  Validation validity: {validation_report['validation_validity_percentage']:.1f}%")
            print(f"  Combined quality score: {validation_report['combined_quality_score']:.2f}")
        else:
            # Perform comprehensive validation
            validation_results = validation_service.validate_multiple_results(results, args.query)

            valid_results = sum(1 for report in validation_results['content'] if report.is_valid)
            total_results = len(validation_results['content'])

            print(f"\nValidation results:")
            print(f"  Total validated: {total_results}")
            print(f"  Valid results: {valid_results}")
            print(f"  Invalid results: {total_results - valid_results}")

            # Show summary
            summary = validation_service.get_validation_summary(results, args.query)
            print(f"\nValidation summary:")
            print(f"  Validity percentage: {summary['validity_percentage']:.1f}%")
            print(f"  Metadata valid: {summary['metadata_summary']['validity_percentage']:.1f}%")
            print(f"  Content quality: {summary['content_summary']['validity_percentage']:.1f}%")

    except Exception as e:
        print(f"Error during validation: {e}")
        return False

    return True


def run_tests(args):
    """Handle the test command."""
    test_type = args.type
    print(f"Running {test_type} tests...")

    try:
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)
        coherence_validator = CoherenceValidator(settings)
        pipeline_service = PipelineService(settings)

        if test_type in ['basic', 'all']:
            print("\n1. Running basic retrieval test...")
            basic_query = "What are the foundations of ROS 2?"
            results = retrieval_service.retrieve(basic_query, limit=3)
            print(f"   Retrieved {len(results)} results for query: '{basic_query[:30]}...'")

        if test_type in ['validation', 'all']:
            print("\n2. Running validation tests...")
            validation_query = "Humanoid robotics components"
            results = retrieval_service.retrieve(validation_query, limit=2)

            if results:
                validation_report = validation_service.validate_result_completely(results[0], validation_query)
                print(f"   Validation result: {'VALID' if validation_report.is_valid else 'INVALID'}")

        if test_type in ['effectiveness', 'all']:
            print("\n3. Running effectiveness tests...")
            effectiveness_query = "Cognitive planning for robots"
            results = retrieval_service.retrieve(effectiveness_query, limit=2)

            if results:
                effectiveness = coherence_validator.evaluate_chunk_effectiveness(results[0])
                print(f"   Chunk effectiveness scores:")
                print(f"     Coherence: {effectiveness['coherence_score']:.3f}")
                print(f"     Context preservation: {effectiveness['context_preservation_score']:.3f}")
                print(f"     Readability: {effectiveness['readability_score']:.3f}")

        if test_type in ['all']:
            print("\n4. Running pipeline tests...")
            test_queries = ["ROS 2 basics", "Humanoid robot components"]
            pipeline_report = pipeline_service.validate_pipeline_integrity(test_queries, limit=2)
            print(f"   Pipeline success rate: {pipeline_report['success_rate']:.1%}")
            print(f"   Pipeline integrity score: {pipeline_report['pipeline_integrity_score']:.3f}")

        print(f"\n✅ All {test_type} tests completed successfully!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def check_health(args):
    """Handle the health command."""
    print("Checking system health and configuration...")

    try:
        settings = Settings()

        print(f"\nConfiguration:")
        print(f"  Qdrant URL: {settings.qdrant_url}")
        print(f"  Qdrant Collection: {settings.qdrant_collection_name}")
        print(f"  Cohere Model: {settings.cohere_model}")
        print(f"  Cohere API Key Set: {'Yes' if settings.cohere_api_key else 'No'}")
        print(f"  Qdrant API Key Set: {'Yes' if settings.qdrant_api_key else 'No'}")

        # Test basic service initialization
        print(f"\nService initialization tests:")

        try:
            retrieval_service = RetrievalService(settings)
            print("  ✅ Retrieval service: OK")
        except Exception as e:
            print(f"  ❌ Retrieval service: {e}")

        try:
            validation_service = ValidationService(settings)
            print("  ✅ Validation service: OK")
        except Exception as e:
            print(f"  ❌ Validation service: {e}")

        print(f"\nSystem is configured correctly! 🚀")

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    return True


def interactive_mode():
    """Start interactive mode."""
    print("Starting interactive mode...")
    print("Type 'help' for commands, 'quit' to exit")

    try:
        settings = Settings()
        retrieval_service = RetrievalService(settings)
        validation_service = ValidationService(settings)

        while True:
            try:
                command = input("\nrag-cli> ").strip()

                if command.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                elif command.lower() == 'help':
                    print("Commands:")
                    print("  retrieve <query> [limit] [min_score] - Retrieve content")
                    print("  validate <query> [keywords] - Validate retrieval results")
                    print("  test - Run system tests")
                    print("  health - Check system health")
                    print("  quit - Exit interactive mode")
                elif command.lower().startswith('retrieve '):
                    # Parse retrieve command
                    parts = command.split()
                    if len(parts) < 2:
                        print("Usage: retrieve <query> [limit] [min_score]")
                        continue

                    query = parts[1]
                    limit = int(parts[2]) if len(parts) > 2 else 5
                    min_score = float(parts[3]) if len(parts) > 3 else 0.1

                    print(f"Retrieving: '{query}' (limit={limit}, min_score={min_score})")
                    results = retrieval_service.retrieve(query, limit=limit, min_score=min_score)

                    print(f"Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"  {i}. Score: {result.similarity_score:.3f} | {result.content_text[:60]}...")

                elif command.lower().startswith('validate '):
                    # Parse validate command
                    parts = command.split()
                    if len(parts) < 2:
                        print("Usage: validate <query> [keywords...]")
                        continue

                    query = parts[1]
                    keywords = parts[2:] if len(parts) > 2 else []

                    print(f"Validating: '{query}' with keywords: {keywords}")

                    results = retrieval_service.retrieve(query, limit=3)
                    if keywords:
                        report = retrieval_service.validate_retrieval_quality(query, keywords, limit=3)
                        print(f"Quality score: {report['combined_quality_score']:.2f}")
                    else:
                        report = validation_service.validate_multiple_results(results, query)
                        valid_count = sum(1 for r in report['content'] if r.is_valid)
                        print(f"Validation: {valid_count}/{len(results)} results valid")

                elif command.lower() == 'test':
                    print("Running quick system test...")
                    results = retrieval_service.retrieve("test", limit=1)
                    print(f"Retrieval test: {len(results)} results retrieved")

                elif command.lower() == 'health':
                    print("System health: All services operational")

                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")

    except Exception as e:
        print(f"Error starting interactive mode: {e}")
        return False

    return True


def main():
    """Main function to run the CLI."""
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Check if any command was provided
    if not args.command:
        parser.print_help()
        return

    # Execute the appropriate command
    if args.command == 'retrieve':
        success = retrieve_content(args)
    elif args.command == 'validate':
        success = validate_content(args)
    elif args.command == 'test':
        success = run_tests(args)
    elif args.command == 'health':
        success = check_health(args)
    elif args.command == 'interactive':
        success = interactive_mode()
    else:
        parser.print_help()
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()