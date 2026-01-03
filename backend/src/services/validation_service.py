"""
Validation Service

This module provides comprehensive validation functionality for the RAG retrieval and validation system.
It combines metadata validation and content validation to provide complete validation reports.
"""
from typing import List, Dict, Any, Optional
from src.config.settings import Settings
from src.models.retrieval_result_model import RetrievalResult
from src.models.validation_report_model import ValidationReport
from src.services.metadata_validator import MetadataValidator
from src.services.content_validator import ContentValidator
from src.services.logging_service import LoggingService
from datetime import datetime
import uuid


class ValidationService:
    """
    Service for performing comprehensive validation on retrieval results.
    Combines metadata alignment validation and content quality validation.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the validation service with settings.
        """
        self.settings = settings
        self.metadata_validator = MetadataValidator(settings)
        self.content_validator = ContentValidator(settings)
        self.logger = LoggingService(settings)

    def validate_retrieval_result(self, result: RetrievalResult, query_text: Optional[str] = None) -> List[ValidationReport]:
        """
        Perform comprehensive validation on a retrieval result.

        Args:
            result: The retrieval result to validate
            query_text: Optional query text for relevance validation

        Returns:
            List[ValidationReport]: List of validation reports (metadata and content)
        """
        validation_id = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # Perform metadata validation
            metadata_report = self.metadata_validator.validate_metadata_alignment(result)

            # Perform content validation
            content_report = self.content_validator.validate_content_quality(result, query_text)

            # Create combined validation summary
            overall_valid = metadata_report.is_valid and content_report.is_valid

            # Log the comprehensive validation
            self.logger.log_validation(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="comprehensive",
                is_valid=overall_valid,
                issues=metadata_report.issues + content_report.issues
            )

            return [metadata_report, content_report]

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="comprehensive_validation",
                error_message=str(e),
                context={
                    "validation_id": validation_id,
                    "result_id": result.result_id
                }
            )
            raise e

    def validate_multiple_results(self, results: List[RetrievalResult], query_text: Optional[str] = None) -> List[ValidationReport]:
        """
        Perform comprehensive validation on multiple retrieval results.

        Args:
            results: List of retrieval results to validate
            query_text: Optional query text for relevance validation

        Returns:
            List[ValidationReport]: List of all validation reports
        """
        all_reports = []
        for result in results:
            reports = self.validate_retrieval_result(result, query_text)
            all_reports.extend(reports)
        return all_reports

    def get_validation_summary(self, results: List[RetrievalResult], query_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a comprehensive validation summary for multiple results.

        Args:
            results: List of retrieval results to validate
            query_text: Optional query text for relevance validation

        Returns:
            Dict[str, Any]: Summary of validation results
        """
        validation_reports = self.validate_multiple_results(results, query_text)

        total_reports = len(validation_reports)
        valid_reports = sum(1 for report in validation_reports if report.is_valid)
        invalid_reports = total_reports - valid_reports

        # Separate metadata and content reports
        metadata_reports = [r for r in validation_reports if r.validation_type == "metadata_alignment"]
        content_reports = [r for r in validation_reports if r.validation_type == "content_quality"]

        # Get individual summaries
        metadata_summary = self.metadata_validator.get_validation_summary(metadata_reports) if metadata_reports else {}
        content_summary = self.content_validator.get_content_quality_summary(content_reports) if content_reports else {}

        # Count all issues
        all_issues = []
        for report in validation_reports:
            all_issues.extend(report.issues)

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        summary = {
            "total_validation_reports": total_reports,
            "valid_reports": valid_reports,
            "invalid_reports": invalid_reports,
            "validity_percentage": (valid_reports / total_reports * 100) if total_reports > 0 else 0,
            "total_issues_found": len(all_issues),
            "unique_issues_count": len(issue_counts),
            "most_common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "metadata_validation_summary": metadata_summary,
            "content_validation_summary": content_summary,
            "timestamp": datetime.now().isoformat()
        }

        return summary

    def validate_pipeline_integrity(self, queries: List[str], limit: int = 5) -> Dict[str, Any]:
        """
        Validate the end-to-end pipeline integrity by running test queries.

        Args:
            queries: List of test queries to run
            limit: Number of results to retrieve per query

        Returns:
            Dict[str, Any]: Pipeline validation report
        """
        from src.services.retrieval_service import RetrievalService

        retrieval_service = RetrievalService(self.settings)
        pipeline_issues = []
        total_results = 0
        valid_results = 0

        for query in queries:
            try:
                # Retrieve results for the query
                results = retrieval_service.retrieve(query_text=query, limit=limit, min_score=0.0)
                total_results += len(results)

                # Validate each result
                for result in results:
                    reports = self.validate_retrieval_result(result, query)
                    if all(report.is_valid for report in reports):
                        valid_results += 1
                    else:
                        pipeline_issues.append(f"Validation failed for query '{query}': {[r.issues for r in reports if r.issues]}")
            except Exception as e:
                pipeline_issues.append(f"Pipeline validation failed for query '{query}': {str(e)}")

        success_rate = valid_results / total_results if total_results > 0 else 0

        pipeline_report = {
            "total_queries": len(queries),
            "total_results": total_results,
            "valid_results": valid_results,
            "success_rate": success_rate,
            "pipeline_issues": pipeline_issues,
            "pipeline_functional": len(pipeline_issues) == 0,
            "timestamp": datetime.now().isoformat()
        }

        # Log the pipeline validation
        self.logger.log_pipeline_validation(
            validation_type="end_to_end",
            metrics=pipeline_report,
            issues=pipeline_issues if pipeline_issues else None
        )

        return pipeline_report