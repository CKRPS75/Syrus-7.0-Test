from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.impact import ImpactCheckRequest, ImpactResponse
from app.services.impact_service import ImpactService
from app.dependencies import get_impact_service

router = APIRouter(tags=["Impact"])


@router.post("/impact/check", response_model=ImpactResponse, status_code=status.HTTP_200_OK, summary="Check disruption impact on a journey")
def check_impact(
    req: ImpactCheckRequest,
    impact_service: ImpactService = Depends(get_impact_service)
):
    try:
        impact = impact_service.check_impact(req)
        return impact
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to check impact: {str(e)}"
        )
