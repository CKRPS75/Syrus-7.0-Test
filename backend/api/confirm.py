from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(
    prefix="/confirm",
    tags=["User Route Confirmation (Person 3 / 4)"]
)

class ConfirmRequest(BaseModel):
    proposal_id: str
    accepted: bool
    is_stale_simulated: bool = False

@router.post("")
def confirm_route_selection(req: ConfirmRequest):
    """
    Handles user confirmation for proposed alternative reroute.
    Enforces freshness and stale route detection.
    """
    if req.is_stale_simulated:
        raise HTTPException(
            status_code=409,
            detail={
                "status": "STALE_PROPOSAL",
                "message": "This route proposal is outdated due to changing traffic conditions. Fetching latest plan...",
                "action": "TRIGGER_REPLAN"
            }
        )

    if req.accepted:
        return {
            "status": "ACCEPTED",
            "message": "New route confirmed. Real-time navigation updated to Alternative Route.",
            "proposal_id": req.proposal_id,
            "active_journey_status": "NAVIGATING_ALTERNATIVE"
        }
    else:
        return {
            "status": "REJECTED",
            "message": "Original route retained. Continuing with current plan.",
            "proposal_id": req.proposal_id,
            "active_journey_status": "NAVIGATING_CURRENT"
        }
