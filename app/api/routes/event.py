import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.event import EventDetailResponse
from app.services.event_service import EventService
from app.dependencies import get_event_service

router = APIRouter(tags=["Event"])


@router.get("/events/{event_id}", response_model=EventDetailResponse, summary="Get event details and associated evidence")
def get_event(
    event_id: uuid.UUID,
    event_service: EventService = Depends(get_event_service)
):
    event = event_service.get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found."
        )
    return event
