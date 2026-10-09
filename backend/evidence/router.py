"""
FastAPI Router for Evidence Processing Endpoint.
Exposes POST /evidence/process and GET /evidence/events for integration with P4 backend.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from backend.evidence.schemas import RawEvidenceInput, ProcessEvidenceResponse, DisruptionEvent
from backend.evidence.pipeline import EvidencePipeline

router = APIRouter(prefix="/evidence", tags=["Evidence & Trust Engine"])
pipeline_instance = EvidencePipeline()


@router.post(
    "/process",
    response_model=ProcessEvidenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Process raw evidence report into structured, trust-weighted disruption event"
)
async def process_evidence_endpoint(payload: RawEvidenceInput) -> ProcessEvidenceResponse:
    """
    Ingests raw crowd, news, or official evidence, performs grounding, deduplication,
    independence checks, freshness decay, and Bayesian trust scoring.
    """
    try:
        response = pipeline_instance.process_evidence(payload)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evidence processing failed: {str(e)}"
        )


@router.get(
    "/events",
    response_model=List[DisruptionEvent],
    summary="List all current disruption events and confidence assessments"
)
async def list_events_endpoint() -> List[DisruptionEvent]:
    """Returns all current active, resolved, or expired disruption events for P3 consumption."""
    return pipeline_instance.get_all_events()


@router.get(
    "/events/{event_id}",
    response_model=DisruptionEvent,
    summary="Get single disruption event assessment by ID"
)
async def get_event_endpoint(event_id: str) -> DisruptionEvent:
    """Retrieves a single disruption event by its identifier (e.g. D01)."""
    ev = pipeline_instance.get_event(event_id)
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found")
    return ev


@router.get(
    "/config/hash",
    response_model=Dict[str, str],
    summary="Retrieve SHA-256 hash of active trust configuration"
)
async def get_config_hash_endpoint() -> Dict[str, str]:
    """Returns configuration hash and version for evaluation reproducibility."""
    return {
        "version": pipeline_instance.config.get("version", "1.0.0"),
        "config_hash": pipeline_instance.get_config_hash()
    }
