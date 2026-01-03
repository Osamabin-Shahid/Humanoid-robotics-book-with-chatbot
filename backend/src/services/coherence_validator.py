"""
Coherence Validator Service

This module provides validation functionality for checking the coherence and contextual
meaning preservation of text chunks in the RAG retrieval and validation system.
"""
from typing import Dict, Any, List, Optional, Tuple
from src.config.settings import Settings
from src.models.retrieval_result_model import RetrievalResult
from src.models.validation_report_model import ValidationReport
from src.services.logging_service import LoggingService
from datetime import datetime
import uuid
import re


class CoherenceValidator:
    """
    Service for validating chunk coherence and contextual meaning preservation.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the coherence validator with settings.
        """
        self.settings = settings
        self.logger = LoggingService(settings)

    def validate_chunk_coherence(self, result: RetrievalResult) -> ValidationReport:
        """
        Validate the coherence of a text chunk to ensure it preserves contextual meaning.

        Args:
            result: The retrieval result containing the chunk to validate

        Returns:
            ValidationReport: Report containing coherence validation results
        """
        validation_id = f"coherence_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        try:
            # Initialize validation flags
            coherence_valid = True
            issues = []

            # Check if content is empty
            if not result.content_text or len(result.content_text.strip()) == 0:
                coherence_valid = False
                issues.append("Content is empty or contains only whitespace")

            # Check for incomplete sentences (potential chunking artifacts)
            incomplete_sentences = self._find_incomplete_sentences(result.content_text)
            if incomplete_sentences:
                coherence_valid = False
                issues.append(f"Chunk contains {len(incomplete_sentences)} incomplete sentence(s)")

            # Check for broken paragraphs or sections
            paragraph_breaks = self._check_paragraph_breaks(result.content_text)
            if paragraph_breaks > 0:
                issues.append(f"Chunk contains {paragraph_breaks} potential paragraph break issues")

            # Check for common chunking artifacts
            artifacts = self._find_chunking_artifacts(result.content_text)
            if artifacts:
                coherence_valid = False
                issues.extend([f"Chunking artifact detected: {artifact}" for artifact in artifacts])

            # Calculate coherence score
            coherence_score = self._calculate_coherence_score(result.content_text)

            # Check for context preservation
            context_preservation_score = self._evaluate_context_preservation(result.content_text)

            # Create validation report
            validation_report = ValidationReport(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="chunk_coherence",
                is_valid=coherence_valid,
                issues=issues,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "coherence_valid": coherence_valid,
                    "content_length": len(result.content_text) if result.content_text else 0,
                    "coherence_score": coherence_score,
                    "context_preservation_score": context_preservation_score,
                    "incomplete_sentences": len(incomplete_sentences),
                    "chunking_artifacts": len(artifacts),
                    "paragraph_breaks": paragraph_breaks
                }
            )

            # Log the validation
            self.logger.log_validation(
                validation_id=validation_id,
                result_id=result.result_id,
                validation_type="chunk_coherence",
                is_valid=validation_report.is_valid,
                issues=issues
            )

            return validation_report

        except Exception as e:
            # Log the error
            self.logger.log_general_error(
                operation_type="coherence_validation",
                error_message=str(e),
                context={
                    "validation_id": validation_id,
                    "result_id": result.result_id
                }
            )
            raise e

    def validate_multiple_chunks(self, results: List[RetrievalResult]) -> List[ValidationReport]:
        """
        Validate coherence for multiple chunks.

        Args:
            results: List of retrieval results to validate

        Returns:
            List[ValidationReport]: List of validation reports
        """
        validation_reports = []
        for result in results:
            report = self.validate_chunk_coherence(result)
            validation_reports.append(report)
        return validation_reports

    def evaluate_chunk_effectiveness(self, result: RetrievalResult) -> Dict[str, Any]:
        """
        Evaluate the overall effectiveness of a chunk beyond just coherence.

        Args:
            result: The retrieval result to evaluate

        Returns:
            Dict[str, Any]: Effectiveness metrics
        """
        coherence_score = self._calculate_coherence_score(result.content_text)
        context_preservation = self._evaluate_context_preservation(result.content_text)
        readability = self._calculate_readability_score(result.content_text)

        # Calculate effectiveness score as average of all metrics
        effectiveness_score = (coherence_score + context_preservation + readability) / 3

        return {
            "coherence_score": coherence_score,
            "context_preservation_score": context_preservation,
            "readability_score": readability,
            "effectiveness_score": effectiveness_score,
            "content_length": len(result.content_text) if result.content_text else 0,
            "word_count": len(result.content_text.split()) if result.content_text else 0,
            "sentence_count": len(self._split_into_sentences(result.content_text))
        }

    def _find_incomplete_sentences(self, text: str) -> List[str]:
        """
        Find incomplete sentences in the text that may indicate chunking artifacts.

        Args:
            text: The text to analyze

        Returns:
            List[str]: List of incomplete sentence fragments
        """
        # Split text into potential sentences
        potential_sentences = re.split(r'[.!?]+', text)

        incomplete_sentences = []
        for sentence in potential_sentences:
            sentence = sentence.strip()
            if sentence:
                # Check if sentence starts with a capital letter
                starts_with_capital = sentence[0].isupper() if sentence else False

                # Check if the original text ended with this sentence fragment
                # (meaning it was cut off mid-sentence)
                if not starts_with_capital and sentence not in text.split('.'):
                    incomplete_sentences.append(sentence)

        # Additional check: sentences that don't end with proper punctuation
        # (assuming the text doesn't end with punctuation)
        if text and text[-1] not in '.!?':
            last_sentence = potential_sentences[-1].strip()
            if last_sentence and last_sentence != potential_sentences[0].strip():
                incomplete_sentences.append(last_sentence)

        return incomplete_sentences

    def _check_paragraph_breaks(self, text: str) -> int:
        """
        Check for issues with paragraph breaks that might indicate chunking problems.

        Args:
            text: The text to analyze

        Returns:
            int: Number of paragraph break issues detected
        """
        # Count occurrences of paragraph-like structures that might be cut off
        issues = 0

        # Check for headers or titles that might be cut off
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line and len(line) < 100:  # Potential header/short line
                # Check if it looks like a header (all caps, or ends mid-sentence without punctuation)
                if line.isupper() and not line.endswith(('.', '!', '?')):
                    issues += 1
                elif len(line) < 20 and not line.endswith(('.', '!', '?')):
                    # Very short line that doesn't end with punctuation
                    issues += 1

        return issues

    def _find_chunking_artifacts(self, text: str) -> List[str]:
        """
        Find common artifacts that indicate problematic chunking.

        Args:
            text: The text to analyze

        Returns:
            List[str]: List of detected chunking artifacts
        """
        artifacts = []

        # Check for common chunking artifacts
        if text.startswith("...") or text.startswith("…"):
            artifacts.append("Begins with ellipsis (possible cut-off)")

        if text.endswith("...") or text.endswith("…"):
            artifacts.append("Ends with ellipsis (possible cut-off)")

        # Check for incomplete references or citations
        if re.search(r'\([^)]*$', text):  # Incomplete parentheses
            artifacts.append("Incomplete parentheses at end of text")

        if re.search(r'["""]*$', text):  # Incomplete quotes
            artifacts.append("Incomplete quotes at end of text")

        # Check for cut-off lists or sequences
        if re.search(r'\d+\.\s*$', text):  # Ends with a numbered list item
            artifacts.append("Ends with numbered list item (possible cut-off)")

        # Check for cut-off bullet points
        if re.search(r'[-*]\s*$', text):  # Ends with bullet point
            artifacts.append("Ends with bullet point (possible cut-off)")

        # Check for incomplete sentences with specific patterns
        if re.search(r'\b(?:and|but|or|so|yet|for|nor)\s*$', text, re.IGNORECASE):
            artifacts.append("Ends with conjunction (possible cut-off mid-sentence)")

        if re.search(r'^\s*(?:and|but|or|so|yet|for|nor)\b', text, re.IGNORECASE):
            artifacts.append("Begins with conjunction (possible cut-off mid-sentence)")

        return artifacts

    def _calculate_coherence_score(self, text: str) -> float:
        """
        Calculate a basic coherence score for the text.

        Args:
            text: The text to analyze

        Returns:
            float: Coherence score between 0 and 1
        """
        if not text:
            return 0.0

        # Calculate various metrics that contribute to coherence
        sentences = self._split_into_sentences(text)
        if not sentences:
            return 0.0

        # Calculate average sentence completeness
        complete_sentences = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence[0].isupper() and sentence[-1] in '.!?':
                complete_sentences += 1

        sentence_completeness = complete_sentences / len(sentences) if sentences else 0

        # Calculate content flow (how well sentences connect)
        content_flow = self._calculate_content_flow(text)

        # Combine metrics for overall coherence score
        coherence_score = (sentence_completeness + content_flow) / 2

        return coherence_score

    def _calculate_content_flow(self, text: str) -> float:
        """
        Calculate how well the content flows from one sentence to another.

        Args:
            text: The text to analyze

        Returns:
            float: Content flow score between 0 and 1
        """
        sentences = self._split_into_sentences(text)
        if len(sentences) < 2:
            return 1.0 if sentences else 0.0

        # Simple approach: check for logical connectors and transitions
        transition_words = [
            'however', 'therefore', 'furthermore', 'additionally', 'meanwhile',
            'consequently', 'nevertheless', 'similarly', 'likewise', 'in contrast',
            'on the other hand', 'as a result', 'for example', 'for instance'
        ]

        text_lower = text.lower()
        transition_count = sum(1 for word in transition_words if word in text_lower)

        # Calculate transition density
        transition_density = transition_count / len(sentences) if sentences else 0

        # A moderate amount of transitions indicates good flow
        # Cap at 1.0 for the flow score
        flow_score = min(1.0, transition_density * 2)  # Adjust multiplier as needed

        return flow_score

    def _evaluate_context_preservation(self, text: str) -> float:
        """
        Evaluate how well the text preserves context and meaning.

        Args:
            text: The text to analyze

        Returns:
            float: Context preservation score between 0 and 1
        """
        if not text:
            return 0.0

        # Check for complete thoughts and concepts
        sentences = self._split_into_sentences(text)
        if not sentences:
            return 0.0

        # Calculate average sentence length to ensure it's not too short
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Check for sufficient content to convey meaning
        word_count = len(text.split())
        min_meaningful_length = 20  # Minimum words for meaningful context

        # Normalize scores
        length_score = min(1.0, word_count / min_meaningful_length)
        avg_length_score = min(1.0, avg_sentence_length / 5)  # Average of 5+ words per sentence is good

        # Combine scores
        context_score = (length_score + avg_length_score) / 2

        return context_score

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

    def get_coherence_summary(self, reports: List[ValidationReport]) -> Dict[str, Any]:
        """
        Get a summary of coherence validation results.

        Args:
            reports: List of validation reports

        Returns:
            Dict[str, Any]: Summary of coherence validation results
        """
        total_validations = len(reports)
        valid_count = sum(1 for report in reports if report.is_valid)
        invalid_count = total_validations - valid_count

        # Extract coherence metrics
        coherence_scores = []
        context_scores = []

        for report in reports:
            if report.metadata:
                if 'coherence_score' in report.metadata:
                    coherence_scores.append(report.metadata['coherence_score'])
                if 'context_preservation_score' in report.metadata:
                    context_scores.append(report.metadata['context_preservation_score'])

        avg_coherence_score = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
        avg_context_score = sum(context_scores) / len(context_scores) if context_scores else 0

        summary = {
            "total_validations": total_validations,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "validity_percentage": (valid_count / total_validations * 100) if total_validations > 0 else 0,
            "avg_coherence_score": avg_coherence_score,
            "avg_context_preservation_score": avg_context_score,
            "timestamp": datetime.now().isoformat()
        }

        return summary