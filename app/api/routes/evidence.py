from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.evidence import EvidenceProcessRequest, EvidenceProcessResponse
from app.services.event_service import EventService
from app.dependencies import get_event_service

router = APIRouter(tags=["Evidence"])


@router.post("/evidence/process", response_model=EvidenceProcessResponse, status_code=status.HTTP_201_CREATED, summary="Process raw evidence/report")
def process_evidence(
    req: EvidenceProcessRequest,
    event_service: EventService = Depends(get_event_service)
):
    try:
        res = event_service.process_evidence(req)
        return res
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process evidence: {str(e)}"
        )
