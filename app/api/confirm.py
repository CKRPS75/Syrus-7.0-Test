from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/confirm",
    tags=["Confirmation"]
)


class ConfirmationRequest(BaseModel):
    confirmed: bool
    journey_id: str
    disruption_confirmed: bool = True
    disruption_active: bool = True


@router.post("")
def confirm_replan(request: ConfirmationRequest):

    if not request.confirmed:
        return {
            "status": "REJECTED",
            "journey_id": request.journey_id,
            "message": (
                "Traveller rejected the proposed journey "
                "and will keep the current journey"
            )
        }

    if not request.journey_id:
        return {
            "status": "REJECTED",
            "reason": "INVALID_JOURNEY",
            "message": "No proposed journey was provided"
        }

    if not request.disruption_confirmed:
        return {
            "status": "STALE",
            "reason": "DISRUPTION_NOT_CONFIRMED",
            "message": (
                "The disruption is no longer confirmed. "
                "Please replan the journey."
            )
        }

    if not request.disruption_active:
        return {
            "status": "STALE",
            "reason": "DISRUPTION_INACTIVE",
            "message": (
                "The disruption is no longer active. "
                "Please replan the journey."
            )
        }

    return {
        "status": "CONFIRMED",
        "journey_id": request.journey_id,
        "message": (
            "Traveller accepted the proposed journey "
            "and the proposal is still valid."
        )
    }