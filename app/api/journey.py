from fastapi import APIRouter, HTTPException

from app.schemas.journey import JourneyRequest
from app.services.otp_service import plan_journey
from app.services.constraint_engine import check_constraints


router = APIRouter(
    prefix="/journey",
    tags=["Journey"]
)


@router.post("/plan")
def create_journey(request: JourneyRequest):

    try:
        journeys = plan_journey(
            origin=request.origin,
            destination=request.destination,
            departure=request.departure
        )

        results = []

        for journey in journeys:

            constraint_result = check_constraints(
                journey,
                request
            )

            results.append({
                "journey": journey,
                "constraint_check": constraint_result
            })

        return {
            "journeys": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )