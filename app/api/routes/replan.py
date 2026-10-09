from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.replan import ReplanRequest, ReplanProposalResponse
from app.services.replan_service import ReplanService
from app.dependencies import get_replan_service

router = APIRouter(tags=["Replan"])


@router.post("/replan", response_model=ReplanProposalResponse, status_code=status.HTTP_201_CREATED, summary="Generate alternative route replan proposal")
def replan(
    req: ReplanRequest,
    replan_service: ReplanService = Depends(get_replan_service)
):
    try:
        proposal = replan_service.create_replan_proposal(req)
        return proposal
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to generate replan proposal: {str(e)}"
        )
