"""
Content Validator Service

This module provides validation functionality for checking the quality of embeddings
and their alignment with source content in the RAG retrieval and validation system.
"""
from typing import Dict, Any, List, Optional
from src.config.settings import Settings
from src.models.retrieval_result_model import RetrievalResult
from src.models.validation_report_model import ValidationReport
from src.services.logging_service import LoggingService
from src.embedding.query_generator import QueryEmbeddingGenerator
from datetime import datetime
import uuid
import re


class ContentValidator:
    """
    Service for validating content quality and embedding alignment.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the content validator with settings.
        """
        self.settings = settings
        self.logger = LoggingService(settings)
        self.query_generator = QueryEmbeddingGenerator(settings)

    def validate_content_quality(self, result: RetrievalResult, query_text: Optional[str] = None) -> ValidationReport:
        """
        Validate the quality of content in a retrieval result.

        Args:
            result: The retrieval result to validate
            query_text: Optional query text for relevance validation

        Returns:
            ValidationReport: Report containing validation results
        """
        validation_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # Initialize validation flags
            quality_valid = True
            issues = []

            # Check content length and quality
            if not result.content_text or len(result.content_text.strip()) == 0:
                quality_valid = False
                issues.append("Content is empty or contains only whitespace")

            elif len(result.content_text.strip()) < 10:  # Minimum content length
                quality_valid = False
                issues.append("Content is too short (less than 10 characters)")

            # Check for special characters or encoding issues
            if self._has_encoding_issues(result.content_text):
                quality_valid = False
                issues.append("Content contains encoding issues")

            # Check for excessive repeated characters (potential chunking issues)
            if self._has_excessive_repetition(result.content_text):
                quality_valid = False
                issues.append("Content contains excessive repetition")

            # Check for readability and coherence
            readability_score = self._calculate_readability_score(result.content_text)
            if readability_score < 0.3:  # Threshold for readability
                quality_valid = False
                issues.append(f"Content readability score too low: {readability_score:.2f}")

            # If query text is provided, check relevance
            relevance_score = 0.0
            if query_text:
                relevance_score = self._calculate_relevance_score(result.content_text, query_text)
                if relevance_score < 0.1:  # Threshold for relevance
                    quality_valid = False
                    issues.append(f"Content relevance to query too low: {relevance_score:.2f}")

            # Create validation report
            validation_report = ValidationReport(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="content_quality",
                is_valid=quality_valid,
                issues=issues,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "quality_valid": quality_valid,
                    "content_length": len(result.content_text) if result.content_text else 0,
                    "readability_score": readability_score,
                    "relevance_score": relevance_score,
                    "similarity_score": result.similarity_score
                }
            )

            # Log the validation
            self.logger.log_validation(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="content_quality",
                is_valid=validation_report.is_valid,
                issues=issues
            )

            return validation_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="content_validation",
                error_message=str(e),
                context={
                    "validation_id": validation_id,
                    "result_id": result.result_id
                }
            )
            raise e

    def validate_content_coherence(self, result: RetrievalResult) -> bool:
        """
        Validate that the content is coherent and makes sense.

        Args:
            result: The retrieval result to validate

        Returns:
            bool: True if content is coherent, False otherwise
        """
        if not result.content_text:
            return False

        # Check if content has proper sentence structure
        sentences = self._split_into_sentences(result.content_text)
        if len(sentences) == 0:
            return False

        # Check if sentences have proper structure (start with capital, end with punctuation)
        proper_sentences = 0
        for sentence in sentences:
            if self._is_proper_sentence(sentence):
                proper_sentences += 1

        # At least 50% of sentences should be properly structured
        coherence_ratio = proper_sentences / len(sentences) if len(sentences) > 0 else 0
        return coherence_ratio >= 0.5

    def validate_content_relevance(self, result: RetrievalResult, query_text: str) -> float:
        """
        Validate the relevance of content to a query.

        Args:
            result: The retrieval result to validate
            query_text: The query to check relevance against

        Returns:
            float: Relevance score between 0 and 1
        """
        if not result.content_text or not query_text:
            return 0.0

        # Calculate relevance using keyword overlap
        query_keywords = set(query_text.lower().split())
        content_words = set(result.content_text.lower().split())

        # Calculate Jaccard similarity
        intersection = query_keywords.intersection(content_words)
        union = query_keywords.union(content_words)

        jaccard_similarity = len(intersection) / len(union) if union else 0.0

        # Also check for semantic similarity using embeddings if possible
        try:
            query_embedding = self.query_generator.get_query_embedding(query_text)
            # For now, we'll use the Jaccard similarity as the relevance score
            # In a real implementation, we would calculate semantic similarity
            # between the query embedding and the content embedding
            return jaccard_similarity
        except:
            # If embedding generation fails, return the Jaccard similarity
            return jaccard_similarity

    def validate_multiple_results(self, results: List[RetrievalResult], query_text: Optional[str] = None) -> List[ValidationReport]:
        """
        Validate content quality for multiple retrieval results.

        Args:
            results: List of retrieval results to validate
            query_text: Optional query text for relevance validation

        Returns:
            List[ValidationReport]: List of validation reports
        """
        validation_reports = []
        for result in results:
            report = self.validate_content_quality(result, query_text)
            validation_reports.append(report)
        return validation_reports

    def _has_encoding_issues(self, content: str) -> bool:
        """
        Check if content has encoding issues.

        Args:
            content: The content to check

        Returns:
            bool: True if encoding issues detected, False otherwise
        """
        try:
            # Try to encode and decode to check for issues
            content.encode('utf-8').decode('utf-8')
            return False
        except UnicodeError:
            return True

    def _has_excessive_repetition(self, content: str) -> bool:
        """
        Check if content has excessive repetition.

        Args:
            content: The content to check

        Returns:
            bool: True if excessive repetition detected, False otherwise
        """
        # Check for repeated characters (more than 5 in a row)
        import re
        repeated_chars = re.findall(r'(.)\1{5,}', content)
        if repeated_chars:
            return True

        # Check for repeated words (more than 3 in a row)
        words = content.split()
        for i in range(len(words) - 3):
            if words[i] == words[i+1] == words[i+2] == words[i+3]:
                return True

        return False

    def _calculate_readability_score(self, content: str) -> float:
        """
        Calculate a basic readability score for the content.

        Args:
            content: The content to analyze

        Returns:
            float: Readability score between 0 and 1
        """
        if not content:
            return 0.0

        # Count sentences, words, and characters
        sentences = len(self._split_into_sentences(content))
        words = len(content.split())
        characters = len(content)

        if sentences == 0 or words == 0:
            return 0.0

        # Calculate average sentence length
        avg_sentence_length = words / sentences

        # Calculate average word length
        avg_word_length = characters / words if words > 0 else 0

        # Basic readability formula (simplified)
        # Score based on reasonable sentence and word lengths
        sentence_score = min(1.0, 20.0 / max(1, avg_sentence_length))
        word_score = min(1.0, 8.0 / max(1, avg_word_length))

        # Combine scores
        readability_score = (sentence_score + word_score) / 2

        return readability_score

    def _calculate_relevance_score(self, content: str, query: str) -> float:
        """
        Calculate a basic relevance score between content and query.

        Args:
            content: The content to check
            query: The query to check against

        Returns:
            float: Relevance score between 0 and 1
        """
        if not content or not query:
            return 0.0

        # Convert to lowercase for comparison
        content_lower = content.lower()
        query_lower = query.lower()

        # Split into words
        content_words = set(content_lower.split())
        query_words = set(query_lower.split())

        # Calculate Jaccard similarity
        intersection = content_words.intersection(query_words)
        union = content_words.union(query_words)

        jaccard_similarity = len(intersection) / len(union) if union else 0.0

        return jaccard_similarity

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: The text to split

        Returns:
            List[str]: List of sentences
        """
        import re
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Remove empty strings and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _is_proper_sentence(self, sentence: str) -> bool:
        """
        Check if a sentence has proper structure.

        Args:
            sentence: The sentence to check

        Returns:
            bool: True if properly structured, False otherwise
        """
        if not sentence:
            return False

        # Check if it starts with a capital letter
        starts_with_capital = sentence[0].isupper() if sentence else False

        # Check if it ends with proper punctuation
        ends_with_punctuation = sentence[-1] in '.!?'

        # Check if it has reasonable length
        has_content = len(sentence.strip()) > 3

        return starts_with_capital and ends_with_punctuation and has_content

    def get_content_quality_summary(self, reports: List[ValidationReport]) -> Dict[str, Any]:
        """
        Get a summary of content quality validation results.

        Args:
            reports: List of validation reports

        Returns:
            Dict[str, Any]: Summary of content quality validation results
        """
        total_validations = len(reports)
        valid_count = sum(1 for report in reports if report.is_valid)
        invalid_count = total_validations - valid_count

        # Extract metadata for summary
        readability_scores = []
        relevance_scores = []
        content_lengths = []

        for report in reports:
            if report.metadata:
                if 'readability_score' in report.metadata:
                    readability_scores.append(report.metadata['readability_score'])
                if 'relevance_score' in report.metadata:
                    relevance_scores.append(report.metadata['relevance_score'])
                if 'content_length' in report.metadata:
                    content_lengths.append(report.metadata['content_length'])

        summary = {
            "total_validations": total_validations,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "validity_percentage": (valid_count / total_validations * 100) if total_validations > 0 else 0,
            "avg_readability_score": sum(readability_scores) / len(readability_scores) if readability_scores else 0,
            "avg_relevance_score": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            "avg_content_length": sum(content_lengths) / len(content_lengths) if content_lengths else 0,
            "timestamp": datetime.now().isoformat()
        }

        return summary