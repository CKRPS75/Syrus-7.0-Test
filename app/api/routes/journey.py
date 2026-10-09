import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.journey import JourneyPlanRequest, JourneyResponse, JourneyDetailResponse
from app.services.journey_service import JourneyService
from app.dependencies import get_journey_service

router = APIRouter(tags=["Journey"])


@router.post("/journey/plan", response_model=JourneyResponse, status_code=status.HTTP_201_CREATED, summary="Plan a new multimodal journey")
def plan_journey(
    req: JourneyPlanRequest,
    journey_service: JourneyService = Depends(get_journey_service)
):
    try:
        journey = journey_service.plan_journey(req)
        return journey
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to plan journey: {str(e)}"
        )


@router.get("/journeys/{journey_id}", response_model=JourneyDetailResponse, summary="Get full journey details")
def get_journey(
    journey_id: uuid.UUID,
    journey_service: JourneyService = Depends(get_journey_service)
):
    journey = journey_service.get_journey(journey_id)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journey with ID {journey_id} not found."
        )

    # Resolve current itinerary
    current_it = None
    if journey.itineraries:
        for it in journey.itineraries:
            if it.id == journey.current_itinerary_id or it.is_current:
                current_it = it
                break

    # Format route impacts and replan proposals as dict lists
    impacts_list = [
        {
            "id": str(imp.id),
            "event_id": str(imp.event_id),
            "affects_route": imp.affects_route,
            "affected_leg": imp.affected_leg,
            "estimated_delay": imp.estimated_delay,
            "route_feasible": imp.route_feasible,
            "route_protected": imp.route_protected,
            "created_at": imp.created_at.isoformat() if imp.created_at else None
        }
        for imp in journey.route_impacts
    ]

    proposals_list = [
        {
            "id": str(prop.id),
            "event_id": str(prop.event_id),
            "old_itinerary_id": str(prop.old_itinerary_id),
            "new_itinerary_id": str(prop.new_itinerary_id),
            "reason": prop.reason,
            "time_saved": prop.time_saved,
            "status": prop.status.value if hasattr(prop.status, 'value') else str(prop.status),
            "created_at": prop.created_at.isoformat() if prop.created_at else None
        }
        for prop in journey.replan_proposals
    ]

    return JourneyDetailResponse(
        id=journey.id,
        traveller_id=journey.traveller_id,
        origin=journey.origin,
        destination=journey.destination,
        departure_time=journey.departure_time,
        status=journey.status,
        current_itinerary_id=journey.current_itinerary_id,
        created_at=journey.created_at,
        updated_at=journey.updated_at,
        traveller=journey.traveller,
        current_itinerary=current_it,
        itineraries=journey.itineraries,
        route_impacts=impacts_list,
        replan_proposals=proposals_list
    )
