"""
Validation API Endpoint

This module provides FastAPI endpoints for the RAG validation functionality.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from src.config.settings import Settings
from src.services.retrieval_service import RetrievalService
from src.services.validation_service import ValidationService
from src.services.coherence_validator import CoherenceValidator
from src.services.pipeline_service import PipelineService
from src.models.retrieval_result_model import RetrievalResult
from src.models.validation_report_model import ValidationReport


# Initialize FastAPI router
router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationRequest(BaseModel):
    """
    Request model for validation endpoint.
    """
    query_text: str
    expected_keywords: Optional[List[str]] = []
    limit: int = Query(10, ge=1, le=100, description="Number of results to validate")
    validate_metadata: bool = Query(True, description="Whether to validate metadata alignment")
    validate_content: bool = Query(True, description="Whether to validate content quality")
    validate_coherence: bool = Query(True, description="Whether to validate chunk coherence")


class ValidationResponse(BaseModel):
    """
    Response model for validation endpoint.
    """
    validation_report: Dict[str, Any]
    is_valid: bool
    issues_found: List[str]
    total_results: int


class PipelineValidationRequest(BaseModel):
    """
    Request model for pipeline validation endpoint.
    """
    test_queries: List[str]
    limit: int = Query(5, ge=1, le=50, description="Number of results per query to validate")
    validate_integrity: bool = Query(True, description="Whether to validate pipeline integrity")
    validate_reproducibility: bool = Query(True, description="Whether to validate reproducibility")


class PipelineValidationResponse(BaseModel):
    """
    Response model for pipeline validation endpoint.
    """
    validation_reports: Dict[str, Any]
    overall_valid: bool
    issues_found: List[str]


def get_settings():
    """
    Dependency to get settings instance.
    """
    return Settings()


def get_validation_service():
    """
    Dependency to get validation service instance.
    """
    settings = get_settings()
    return ValidationService(settings)


def get_retrieval_service():
    """
    Dependency to get retrieval service instance.
    """
    settings = get_settings()
    return RetrievalService(settings)


def get_coherence_validator():
    """
    Dependency to get coherence validator instance.
    """
    settings = get_settings()
    return CoherenceValidator(settings)


def get_pipeline_service():
    """
    Dependency to get pipeline service instance.
    """
    settings = get_settings()
    return PipelineService(settings)


@router.post("/validate-retrieval", response_model=ValidationResponse, summary="Validate retrieval quality")
async def validate_retrieval(
    request: ValidationRequest,
    validation_service: ValidationService = Depends(get_validation_service),
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Validate the quality of retrieval results against expected content and validation criteria.

    Args:
        request: The validation request containing query and validation parameters
        validation_service: The validation service instance
        retrieval_service: The retrieval service instance

    Returns:
        ValidationResponse: The validation results
    """
    try:
        import time
        start_time = time.time()

        # Retrieve results first
        results = retrieval_service.retrieve(
            query_text=request.query_text,
            limit=request.limit
        )

        # Perform validation based on request parameters
        validation_results = []
        all_issues = []

        for result in results:
            # Perform comprehensive validation
            validation_report = validation_service.validate_result_completely(
                result, request.query_text
            )
            validation_results.append(validation_report)
            if not validation_report.is_valid:
                all_issues.extend(validation_report.issues)

        # Get summary of validation
        summary = validation_service.get_validation_summary(results, request.query_text)

        # Calculate overall validity
        overall_valid = len(all_issues) == 0

        response = ValidationResponse(
            validation_report=summary,
            is_valid=overall_valid,
            issues_found=all_issues,
            total_results=len(results)
        )

        execution_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Validation completed in {execution_time_ms:.2f}ms for query: {request.query_text[:50]}...")
        return response

    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/validate-content", summary="Validate content quality")
async def validate_content(
    request: ValidationRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Validate the quality of content in retrieval results.

    Args:
        request: The validation request containing query and parameters
        retrieval_service: The retrieval service instance

    Returns:
        dict: Content validation results
    """
    try:
        import time
        start_time = time.time()

        # Retrieve results
        results = retrieval_service.retrieve(
            query_text=request.query_text,
            limit=request.limit
        )

        # Validate content quality
        from src.services.content_validator import ContentValidator
        settings = get_settings()
        content_validator = ContentValidator(settings)

        validation_reports = content_validator.validate_multiple_results(
            results, request.query_text
        )

        # Calculate summary
        content_summary = content_validator.get_content_quality_summary(validation_reports)

        execution_time_ms = (time.time() - start_time) * 1000

        response = {
            "results_validated": len(results),
            "content_validation_reports": [report.dict() for report in validation_reports],
            "content_summary": content_summary,
            "execution_time_ms": round(execution_time_ms, 2)
        }

        logger.info(f"Content validation completed for {len(results)} results")
        return response

    except Exception as e:
        logger.error(f"Error during content validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content validation failed: {str(e)}")


@router.post("/validate-metadata", summary="Validate metadata alignment")
async def validate_metadata(
    request: ValidationRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Validate the alignment of metadata in retrieval results.

    Args:
        request: The validation request containing query and parameters
        retrieval_service: The retrieval service instance

    Returns:
        dict: Metadata validation results
    """
    try:
        import time
        start_time = time.time()

        # Retrieve results
        results = retrieval_service.retrieve(
            query_text=request.query_text,
            limit=request.limit
        )

        # Validate metadata alignment
        from src.services.metadata_validator import MetadataValidator
        settings = get_settings()
        metadata_validator = MetadataValidator(settings)

        validation_reports = metadata_validator.validate_multiple_results(results)

        # Calculate summary
        metadata_summary = metadata_validator.get_validation_summary(validation_reports)

        execution_time_ms = (time.time() - start_time) * 1000

        response = {
            "results_validated": len(results),
            "metadata_validation_reports": [report.dict() for report in validation_reports],
            "metadata_summary": metadata_summary,
            "execution_time_ms": round(execution_time_ms, 2)
        }

        logger.info(f"Metadata validation completed for {len(results)} results")
        return response

    except Exception as e:
        logger.error(f"Error during metadata validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metadata validation failed: {str(e)}")


@router.post("/validate-coherence", summary="Validate chunk coherence")
async def validate_coherence(
    request: ValidationRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    coherence_validator: CoherenceValidator = Depends(get_coherence_validator)
):
    """
    Validate the coherence of text chunks in retrieval results.

    Args:
        request: The validation request containing query and parameters
        retrieval_service: The retrieval service instance
        coherence_validator: The coherence validator instance

    Returns:
        dict: Coherence validation results
    """
    try:
        import time
        start_time = time.time()

        # Retrieve results
        results = retrieval_service.retrieve(
            query_text=request.query_text,
            limit=request.limit
        )

        # Validate chunk coherence
        validation_reports = coherence_validator.validate_multiple_chunks(results)

        # Calculate summary
        coherence_summary = coherence_validator.get_coherence_summary(validation_reports)

        execution_time_ms = (time.time() - start_time) * 1000

        response = {
            "results_validated": len(results),
            "coherence_validation_reports": [report.dict() for report in validation_reports],
            "coherence_summary": coherence_summary,
            "execution_time_ms": round(execution_time_ms, 2)
        }

        logger.info(f"Coherence validation completed for {len(results)} results")
        return response

    except Exception as e:
        logger.error(f"Error during coherence validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Coherence validation failed: {str(e)}")


@router.post("/validate-pipeline", response_model=PipelineValidationResponse, summary="Validate pipeline integrity")
async def validate_pipeline(
    request: PipelineValidationRequest,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Validate the integrity and effectiveness of the entire RAG pipeline.

    Args:
        request: The pipeline validation request containing test queries and parameters
        pipeline_service: The pipeline service instance

    Returns:
        PipelineValidationResponse: The pipeline validation results
    """
    try:
        import time
        start_time = time.time()

        validation_reports = {}

        # Validate pipeline integrity
        if request.validate_integrity:
            integrity_report = pipeline_service.validate_pipeline_integrity(
                request.test_queries,
                request.limit
            )
            validation_reports["integrity"] = integrity_report

        # Validate reproducibility
        if request.validate_reproducibility and request.test_queries:
            # Use the first query for reproducibility testing
            reproducibility_report = pipeline_service.validate_pipeline_reproducibility(
                request.test_queries[0],
                num_runs=3
            )
            validation_reports["reproducibility"] = reproducibility_report

        # Determine overall validity
        overall_valid = all(
            report.get("success_rate", 1) >= 0.8 if "success_rate" in report
            else report.get("reproducible", True)
            for report in validation_reports.values()
        )

        # Collect all issues
        all_issues = []
        for report in validation_reports.values():
            if "pipeline_issues" in report and report["pipeline_issues"]:
                all_issues.extend(report["pipeline_issues"])

        response = PipelineValidationResponse(
            validation_reports=validation_reports,
            overall_valid=overall_valid,
            issues_found=all_issues
        )

        execution_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Pipeline validation completed in {execution_time_ms:.2f}ms")
        return response

    except Exception as e:
        logger.error(f"Error during pipeline validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline validation failed: {str(e)}")


@router.get("/validation/health", summary="Validation service health check")
async def validation_health_check():
    """
    Health check endpoint for the validation service.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "RAG Validation API",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }