#!/usr/bin/env python3
"""
Main execution script for the RAG agent.
Accepts user queries and returns grounded responses based on book content.
"""

import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import rag_agent
from services.logging_service import logging_service
from config.settings import settings
from services.local_execution import LocalExecutionService


def main():
    """
    Main function to run the RAG agent in interactive mode.
    """
    parser = argparse.ArgumentParser(description='RAG Agent for Book Content Queries')
    parser.add_argument('--mode', choices=['interactive', 'test', 'health'], default='interactive',
                        help='Run mode: interactive (default), test, or health check')
    parser.add_argument('--query', type=str, help='Single query to process (for non-interactive mode)')
    parser.add_argument('--batch', nargs='+', help='Multiple queries to process in batch')

    args = parser.parse_args()

    # Initialize local execution service
    local_service = LocalExecutionService()

    if args.mode == 'health':
        print("Running health check...")
        health_status = local_service.test_connection_health()
        print(f"Health status: {health_status}")
        return

    if args.mode == 'test':
        print("Running in test mode...")
        if args.query:
            # Run single test query
            response = local_service.run_test_query(args.query)
            print(f"Test response: {response.content}")
        elif args.batch:
            # Run batch of test queries
            responses = local_service.run_batch_queries(args.batch)
            for i, response in enumerate(responses, 1):
                print(f"Query {i} response: {response.content[:100]}...")
        else:
            # Run system info and basic tests
            print("System Info:")
            system_info = local_service.get_system_info()
            print(f"  Python Version: {system_info['python_version'][:50]}...")
            print(f"  Qdrant Collection: {system_info['settings']['qdrant_collection_name']}")
            print(f"  Configured Services: {system_info['configured_services']}")
        return

    # Default interactive mode
    print("RAG Agent - Book Content Query System")
    print("=====================================")
    print("Type your questions about the book content, or 'quit' to exit.\n")

    # Check if the agent is properly configured
    health_status = rag_agent.check_health()
    if not health_status["qdrant_connected"]:
        print("WARNING: Cannot connect to Qdrant. Please check your configuration.")
        print("Ensure QDRANT_URL and QDRANT_API_KEY are set in your .env file.")
        return

    print("Agent is ready to answer questions!\n")

    while True:
        try:
            # Get user input
            query = input("Enter your question: ").strip()

            # Check for exit condition
            if query.lower() in ['quit', 'exit', 'q']:
                print("Thank you for using the RAG Agent. Goodbye!")
                break

            # Skip empty queries
            if not query:
                print("Please enter a question.\n")
                continue

            # Process the query using the RAG agent
            response = rag_agent.process_query(query)

            # Display the response
            print(f"\nResponse: {response.content}")
            if response.confidence_score > 0:
                print(f"Confidence: {response.confidence_score:.2f}")
            print()

        except KeyboardInterrupt:
            print("\n\nThank you for using the RAG Agent. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.\n")


def run_query(query_text: str):
    """
    Function to run a single query and return the response.
    Useful for testing or programmatic use.

    Args:
        query_text: The query text to process

    Returns:
        AgentResponse object with the result
    """
    # Check if the agent is properly configured
    health_status = rag_agent.check_health()
    if not health_status["qdrant_connected"]:
        print("ERROR: Cannot connect to Qdrant. Please check your configuration.")
        return None

    # Process the query
    response = rag_agent.process_query(query_text)
    return response


if __name__ == "__main__":
    main()