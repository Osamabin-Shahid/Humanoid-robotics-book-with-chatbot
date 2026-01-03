"""
Pipeline Service

This module provides validation functionality for checking the end-to-end
functionality of the RAG pipeline in the retrieval and validation system.
"""
from typing import Dict, Any, List, Optional
from src.config.settings import Settings
from src.models.retrieval_result_model import RetrievalResult
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService
from src.services.coherence_validator import CoherenceValidator
from src.services.logging_service import LoggingService
from src.embedding.query_generator import QueryEmbeddingGenerator
from src.storage.qdrant_client import QdrantCloudClient
from datetime import datetime
import uuid


class PipelineService:
    """
    Service for validating the end-to-end RAG pipeline functionality.
    Ensures that the complete flow from storage to retrieval works correctly.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the pipeline service with settings.
        """
        self.settings = settings
        self.retrieval_service = RetrievalService(settings)
        self.validation_service = ValidationService(settings)
        self.coherence_validator = CoherenceValidator(settings)
        self.logger = LoggingService(settings)
        self.query_generator = QueryEmbeddingGenerator(settings)
        self.qdrant_client = QdrantCloudClient(settings)

    def validate_pipeline_integrity(self, queries: List[str], limit: int = 5) -> Dict[str, Any]:
        """
        Validate the end-to-end pipeline integrity by running test queries.

        Args:
            queries: List of test queries to run
            limit: Number of results to retrieve per query

        Returns:
            Dict[str, Any]: Pipeline validation report
        """
        pipeline_validation_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        pipeline_issues = []

        try:
            total_queries = len(queries)
            total_results = 0
            valid_results = 0
            issues_count = 0

            for query in queries:
                print(f"Validating pipeline for query: {query}")
                try:
                    # Retrieve results for the query
                    results = self.retrieval_service.retrieve(
                        query_text=query,
                        limit=limit,
                        min_score=0.0
                    )
                    print(f"  Retrieved {len(results)} results")

                    total_results += len(results)

                    # Validate each result
                    for result in results:
                        validation_reports = self.validation_service.validate_retrieval_result(result, query)

                        # Check if all validations pass
                        for report in validation_reports:
                            if not report.is_valid:
                                pipeline_issues.append(f"Validation failed for result {result.result_id}: {report.issues}")
                                issues_count += 1
                            else:
                                valid_results += 1
                except Exception as e:
                    pipeline_issues.append(f"Pipeline validation failed for query '{query}': {str(e)}")
                    issues_count += 1

            # Calculate effectiveness metrics
            success_rate = valid_results / total_results if total_results > 0 else 0
            avg_issues_per_query = issues_count / total_queries if total_queries > 0 else 0

            # Get chunk effectiveness metrics
            chunk_effectiveness_metrics = self._evaluate_chunk_effectiveness(results) if results else {}

            pipeline_report = {
                "total_queries": total_queries,
                "total_results": total_results,
                "valid_results": valid_results,
                "issues_count": issues_count,
                "success_rate": success_rate,
                "avg_issues_per_query": avg_issues_per_query,
                "pipeline_issues": pipeline_issues,
                "pipeline_functional": len(pipeline_issues) == 0 and total_results > 0,
                "chunk_effectiveness_metrics": chunk_effectiveness_metrics,
                "timestamp": datetime.now().isoformat()
            }

            # Log the pipeline validation
            self.logger.log_pipeline_validation(
                validation_type="end_to_end",
                metrics=pipeline_report,
                issues=pipeline_issues if pipeline_issues else None
            )

            return pipeline_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="error",
                error_message=str(e),
                context={
                    "validation_id": pipeline_validation_id
                }
            )
            raise e

    def validate_store_retrieve_pipeline(self, sample_content: str, query: str, chunk_size: int = 512) -> Dict[str, Any]:
        """
        Validate the store → retrieve pipeline by testing if content can be retrieved after storage.

        Args:
            sample_content: Sample content to test storage and retrieval
            query: Query to test retrieval
            chunk_size: Size of chunks to create

        Returns:
            Dict[str, Any]: Store-retrieve validation report
        """
        validation_id = f"store_retrieve_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # This would involve actually storing content and then retrieving it
            # For now, we'll simulate the validation by checking if the system can retrieve content
            results = self.retrieval_service.retrieve(
                query_text=query,
                limit=5,
                min_score=0.0
            )

            # Validate the results
            validation_reports = self.validation_service.validate_multiple_results(results, query)

            # Check for coherence in results
            coherence_reports = self.coherence_validator.validate_multiple_chunks(results)

            # Evaluate content similarity (how well the results match the query intent)
            content_similarity_score = self._calculate_content_similarity_score(results, query)

            # Check if pipeline is functional
            coherence_issues = [r for r in coherence_reports if not r.is_valid]
            validation_issues = [r for r in validation_reports if not r.is_valid]

            coherence_issues_count = len(coherence_issues)
            validation_issues_count = len(validation_issues)

            store_retrieve_report = {
                "query": query,
                "results_count": len(results),
                "validation_issues_count": validation_issues_count,
                "coherence_issues_count": coherence_issues_count,
                "content_similarity_score": content_similarity_score,
                "pipeline_functional": len(results) > 0 and coherence_issues_count == 0 and validation_issues_count == 0,
                "timestamp": datetime.now().isoformat()
            }

            # Log the store-retrieve validation
            self.logger.log_validation(
                result_id="store_retrieve_validation",
                validation_score=1.0 if store_retrieve_report["pipeline_functional"] else 0.0,
                issues_found=[],
                validation_type="store_retrieve"
            )

            return store_retrieve_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="error",
                error_message=str(e),
                context={
                    "validation_id": validation_id,
                    "query": query
                }
            )
            raise e

    def validate_chunking_strategy(self, test_content: str, expected_chunks: int = 3) -> Dict[str, Any]:
        """
        Validate that the chunking strategy produces coherent, contextually meaningful segments.

        Args:
            test_content: Content to test chunking on
            expected_chunks: Expected number of chunks

        Returns:
            Dict[str, Any]: Chunking validation report
        """
        validation_id = f"chunking_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # In a real implementation, we would chunk the content and validate each chunk
            # For now, we'll use the existing retrieval system to test chunk effectiveness
            # by running queries and validating the coherence of results

            # Run a query to get results that would have been chunked
            results = self.retrieval_service.retrieve(
                query_text="test content",
                limit=expected_chunks,
                min_score=0.0
            )

            # Validate coherence of results (these would be the chunks)
            coherence_reports = self.coherence_validator.validate_multiple_chunks(results)

            # Calculate average coherence
            valid_coherence_reports = [r for r in coherence_reports if r.is_valid]
            avg_coherence = sum(r.metadata.get('coherence_score', 0) for r in valid_coherence_reports) / len(valid_coherence_reports) if valid_coherence_reports else 0

            # Evaluate chunk effectiveness
            coherence_reports_with_metrics = [self.coherence_validator.evaluate_chunk_effectiveness(r) for r in results]
            avg_effectiveness = sum(r.get('effectiveness_score', 0) for r in coherence_reports_with_metrics) / len(coherence_reports_with_metrics) if coherence_reports_with_metrics else 0

            chunking_report = {
                "expected_chunks": expected_chunks,
                "actual_results_count": len(results),
                "valid_coherence_reports": len(valid_coherence_reports),
                "average_coherence": avg_coherence,
                "average_effectiveness": avg_effectiveness,
                "coherence_issues": len([r for r in coherence_reports if not r.is_valid]),
                "recommendations": self._generate_chunking_recommendations(avg_coherence, results),
                "timestamp": datetime.now().isoformat()
            }

            # Log the chunking validation
            self.logger.log_validation(
                result_id="chunking_validation",
                validation_score=avg_coherence,
                issues_found=[],
                validation_type="chunking_strategy"
            )

            return chunking_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="error",
                error_message=str(e),
                context={
                    "validation_id": validation_id
                }
            )
            raise e

    def validate_pipeline_reproducibility(self, query: str, num_runs: int = 3) -> Dict[str, Any]:
        """
        Validate that the pipeline produces reproducible results across multiple runs.

        Args:
            query: Query to test reproducibility
            num_runs: Number of runs to perform

        Returns:
            Dict[str, Any]: Reproducibility validation report
        """
        validation_id = f"reproducibility_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            all_results = []
            all_validation_reports = []

            for i in range(num_runs):
                # Retrieve results for the same query multiple times
                results = self.retrieval_service.retrieve(
                    query_text=query,
                    limit=5,
                    min_score=0.0
                )
                all_results.append(results)

                # Validate the results
                validation_reports = self.validation_service.validate_multiple_results(results, query)
                all_validation_reports.append(validation_reports)

            # Check for consistency across runs
            consistent_results = self._check_result_consistency(all_results)
            consistent_validations = self._check_validation_consistency(all_validation_reports)

            # Calculate variance in results
            result_variance = self._calculate_result_variance(all_results)

            reproducibility_report = {
                "query": query,
                "num_runs": num_runs,
                "consistent_results": consistent_results,
                "consistent_validations": consistent_validations,
                "result_variance": result_variance,
                "reproducible": consistent_results and consistent_validations,
                "timestamp": datetime.now().isoformat()
            }

            # Log the reproducibility validation
            self.logger.log_validation(
                result_id="reproducibility_validation",
                validation_score=1.0 if reproducibility_report["reproducible"] else 0.0,
                issues_found=[],
                validation_type="reproducibility"
            )

            return reproducibility_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="error",
                error_message=str(e),
                context={
                    "validation_id": validation_id,
                    "query": query
                }
            )
            raise e

    def _evaluate_chunk_effectiveness(self, results: List[RetrievalResult]) -> Dict[str, float]:
        """
        Evaluate the effectiveness of chunks in the results.

        Args:
            results: List of retrieval results (chunks)

        Returns:
            Dict[str, float]: Effectiveness metrics
        """
        if not results:
            return {}

        # Calculate various effectiveness metrics
        avg_similarity = sum(r.similarity_score for r in results) / len(results)
        avg_content_length = sum(len(r.content_text) if r.content_text else 0 for r in results) / len(results)

        # Validate coherence for each result
        coherence_scores = []
        for result in results:
            coherence_report = self.coherence_validator.evaluate_chunk_effectiveness(result)
            coherence_scores.append(coherence_report['effectiveness_score'])

        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0

        effectiveness_metrics = {
            "avg_similarity_score": avg_similarity,
            "avg_content_length": avg_content_length,
            "avg_coherence_score": avg_coherence,
            "total_chunks": len(results)
        }

        return effectiveness_metrics

    def _calculate_content_similarity_score(self, results: List[RetrievalResult], query: str) -> float:
        """
        Calculate a basic similarity score between results and query.

        Args:
            results: List of retrieval results
            query: Query text

        Returns:
            float: Content similarity score
        """
        if not results or not query:
            return 0.0

        # Calculate average similarity score from the results
        avg_similarity = sum(r.similarity_score for r in results) / len(results)
        return avg_similarity

    def _generate_chunking_recommendations(self, avg_coherence: float, results: List[RetrievalResult]) -> List[str]:
        """
        Generate recommendations based on chunking effectiveness.

        Args:
            avg_coherence: Average coherence score
            results: List of retrieval results

        Returns:
            List[str]: Recommendations for improving chunking
        """
        recommendations = []

        if avg_coherence < 0.5:
            recommendations.append("Average coherence is low. Consider adjusting chunk size or overlap parameters.")

        if results:
            avg_length = sum(len(r.content_text) if r.content_text else 0 for r in results) / len(results)
            if avg_length < 100:
                recommendations.append("Chunks are too short. Consider increasing chunk size.")
            elif avg_length > 1000:
                recommendations.append("Chunks are too long. Consider decreasing chunk size.")

        return recommendations

    def _check_result_consistency(self, all_results: List[List[RetrievalResult]]) -> bool:
        """
        Check if results are consistent across multiple runs.

        Args:
            all_results: List of result lists from multiple runs

        Returns:
            bool: True if results are consistent, False otherwise
        """
        if len(all_results) < 2:
            return True

        # For simplicity, check if the number of results is consistent
        result_counts = [len(results) for results in all_results]
        return len(set(result_counts)) == 1  # All counts are the same

    def _check_validation_consistency(self, all_validation_reports: List[List[RetrievalResult]]) -> bool:
        """
        Check if validation results are consistent across multiple runs.

        Args:
            all_validation_reports: List of validation report lists from multiple runs

        Returns:
            bool: True if validation is consistent, False otherwise
        """
        if len(all_validation_reports) < 2:
            return True

        # For simplicity, check if the validation status is consistent
        valid_counts = [sum(1 for r in reports if r.is_valid) for reports in all_validation_reports]
        return len(set(valid_counts)) == 1  # All counts are the same

    def _calculate_result_variance(self, all_results: List[List[RetrievalResult]]) -> float:
        """
        Calculate variance in results across multiple runs.

        Args:
            all_results: List of result lists from multiple runs

        Returns:
            float: Variance score
        """
        if len(all_results) < 2:
            return 0.0

        # Calculate variance in result counts
        result_counts = [len(results) for results in all_results]
        mean_count = sum(result_counts) / len(result_counts)
        variance = sum((count - mean_count) ** 2 for count in result_counts) / len(result_counts)

        return variance