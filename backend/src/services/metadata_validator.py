"""
Metadata Validator Service

This module provides validation functionality for checking alignment between embeddings
and their source content, metadata, and URLs in the RAG retrieval and validation system.
"""
from typing import Dict, Any, List, Optional
from src.config.settings import Settings
from src.models.retrieval_result_model import RetrievalResult
from src.models.validation_report_model import ValidationReport
from src.services.logging_service import LoggingService
from datetime import datetime
import uuid


class MetadataValidator:
    """
    Service for validating metadata alignment between embeddings and source content.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the metadata validator with settings.
        """
        self.settings = settings
        self.logger = LoggingService(settings)

    def validate_metadata_alignment(self, result: RetrievalResult) -> ValidationReport:
        """
        Validate that the metadata in a retrieval result aligns with expected values.

        Args:
            result: The retrieval result to validate

        Returns:
            ValidationReport: Report containing validation results
        """
        validation_id = f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # Initialize validation flags
            alignment_valid = True
            issues = []

            # Check if source URL is valid and properly formatted
            if not result.source_url or not self._is_valid_url(result.source_url):
                alignment_valid = False
                issues.append("Invalid or missing source URL")

            # Check if chunk ID exists and is properly formatted
            if not result.chunk_id:
                alignment_valid = False
                issues.append("Missing chunk ID")

            # Check if content text exists
            if not result.content_text or len(result.content_text.strip()) == 0:
                alignment_valid = False
                issues.append("Missing or empty content text")

            # Check if similarity score is within valid range
            if result.similarity_score is None or result.similarity_score < 0 or result.similarity_score > 1:
                alignment_valid = False
                issues.append("Invalid similarity score (must be between 0 and 1)")

            # Check if metadata exists and has required fields
            metadata_valid = True
            if not result.metadata:
                metadata_valid = False
                issues.append("Missing metadata")
            else:
                required_metadata_fields = ['source_url', 'chunk_id', 'content', 'created_at']
                for field in required_metadata_fields:
                    if field not in result.metadata:
                        metadata_valid = False
                        issues.append(f"Missing required metadata field: {field}")

                # Check if metadata fields align with result properties
                if result.metadata.get('source_url') != result.source_url:
                    alignment_valid = False
                    issues.append("Metadata source_url does not match result source_url")

                if result.metadata.get('chunk_id') != result.chunk_id:
                    alignment_valid = False
                    issues.append("Metadata chunk_id does not match result chunk_id")

                if result.metadata.get('content') != result.content_text:
                    alignment_valid = False
                    issues.append("Metadata content does not match result content_text")

            # Create validation report
            validation_report = ValidationReport(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="metadata_alignment",
                is_valid=alignment_valid and metadata_valid,
                issues=issues,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "alignment_valid": alignment_valid,
                    "metadata_valid": metadata_valid,
                    "result_source_url": result.source_url,
                    "result_chunk_id": result.chunk_id,
                    "content_length": len(result.content_text) if result.content_text else 0,
                    "similarity_score": result.similarity_score
                }
            )

            # Log the validation
            self.logger.log_validation(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="metadata_alignment",
                is_valid=validation_report.is_valid,
                issues=issues
            )

            return validation_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="metadata_validation",
                error_message=str(e),
                context={
                    "validation_id": validation_id,
                    "result_id": result.result_id
                }
            )
            raise e

    def validate_multiple_results(self, results: List[RetrievalResult]) -> List[ValidationReport]:
        """
        Validate metadata alignment for multiple retrieval results.

        Args:
            results: List of retrieval results to validate

        Returns:
            List[ValidationReport]: List of validation reports
        """
        validation_reports = []
        for result in results:
            report = self.validate_metadata_alignment(result)
            validation_reports.append(report)
        return validation_reports

    def validate_source_url_alignment(self, result: RetrievalResult) -> bool:
        """
        Validate that the source URL in the result aligns with expected patterns.

        Args:
            result: The retrieval result to validate

        Returns:
            bool: True if source URL is valid, False otherwise
        """
        if not result.source_url:
            return False

        return self._is_valid_url(result.source_url)

    def validate_content_alignment(self, result: RetrievalResult) -> bool:
        """
        Validate that the content in the result aligns with its metadata.

        Args:
            result: The retrieval result to validate

        Returns:
            bool: True if content alignment is valid, False otherwise
        """
        if not result.content_text or not result.metadata:
            return False

        # Check if content in metadata matches the content_text
        metadata_content = result.metadata.get('content', '')
        return metadata_content == result.content_text

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is properly formatted.

        Args:
            url: The URL to validate

        Returns:
            bool: True if valid, False otherwise
        """
        import re
        # Simple URL validation regex
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return url_pattern.match(url) is not None

    def get_validation_summary(self, reports: List[ValidationReport]) -> Dict[str, Any]:
        """
        Get a summary of validation results.

        Args:
            reports: List of validation reports

        Returns:
            Dict[str, Any]: Summary of validation results
        """
        total_validations = len(reports)
        valid_count = sum(1 for report in reports if report.is_valid)
        invalid_count = total_validations - valid_count

        # Count specific issues
        all_issues = []
        for report in reports:
            all_issues.extend(report.issues)

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        summary = {
            "total_validations": total_validations,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "validity_percentage": (valid_count / total_validations * 100) if total_validations > 0 else 0,
            "most_common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "timestamp": datetime.now().isoformat()
        }

        return summary