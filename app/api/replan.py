from fastapi import APIRouter

from app.schemas.replan import ReplanRequest
from app.services.otp_service import plan_journey
from app.models.disruption import Disruption
from app.services.impact_engine import check_impact
from app.services.alternative_service import generate_alternative
from app.services.stability import should_propose_alternative
from app.services.delay_model import calculate_delay
from app.services.constraint_engine import check_constraints
from app.schemas.journey import JourneyRequest
from app.services.report_processor import process_crowd_reports


router = APIRouter(
    prefix="/replan",
    tags=["Replanning"]
)


@router.post("")
def replan_journey(request: ReplanRequest):

    try:

        # Process current crowd reports
        report_result = process_crowd_reports(
            official_confirmed=request.confirmed,
            news_confirmed=False
        )

        confidence = report_result["confidence"]

        # Do not replan on low-confidence disruption
        if not request.confirmed and confidence < 0.70:
            return {
                "decision": "KEEP",
                "reason": "Disruption confidence is too low",
                "confidence": confidence,
                "confirmation_required": False
            }

        journeys = plan_journey(
            origin=request.origin,
            destination=request.destination,
            departure=request.departure
        )

        if not journeys:
            return {
                "decision": "INFEASIBLE",
                "reason": "OTP returned no journeys"
            }

        current_journey = journeys[0]

        traveller_request = JourneyRequest(
            origin=request.origin,
            destination=request.destination,
            departure=request.departure,
            deadline=request.deadline,
            budget=request.budget,
            max_walking=request.max_walking,
            transfer_tolerance=request.transfer_tolerance,
            forbidden_modes=request.forbidden_modes
        )

        current_constraints = check_constraints(
            current_journey,
            traveller_request
        )

        disruption = Disruption(
            disruption_id="D001",
            route_name=request.route_name,
            disruption_type=request.disruption_type,
            severity=request.severity,
            confirmed=request.confirmed,
            active=request.active
        )

        if not disruption.confirmed:
            return {
                "decision": "KEEP",
                "reason": "Disruption is not confirmed",
                "confidence": confidence
            }

        if not disruption.active:
            return {
                "decision": "KEEP",
                "reason": "Disruption is no longer active",
                "confidence": confidence
            }

        impact = check_impact(
            current_journey,
            disruption
        )

        if not impact["affected"]:
            return {
                "decision": "KEEP",
                "reason": "Disruption does not affect current journey",
                "current_journey": current_journey,
                "constraint_check": current_constraints,
                "impact": impact,
                "confidence": confidence
            }

        alternative_result = generate_alternative(
            current_journey,
            disruption
        )

        if not alternative_result["alternative_found"]:
            return {
                "decision": "INFEASIBLE",
                "reason": "No alternative was found",
                "current_journey": current_journey,
                "impact": impact,
                "confidence": confidence
            }

        alternative_journey = alternative_result["journey"]

        alternative_constraints = check_constraints(
            alternative_journey,
            traveller_request
        )

        if not alternative_constraints["feasible"]:
            return {
                "decision": "KEEP",
                "reason": "Alternative violates traveller constraints",
                "current_journey": current_journey,
                "alternative": alternative_journey,
                "alternative_constraints": alternative_constraints,
                "confidence": confidence
            }

        disruption_delay = calculate_delay(
            disruption.severity
        )

        comparison = should_propose_alternative(
            current_journey=current_journey,
            alternative_journey=alternative_journey,
            current_deadline_status=current_constraints[
                "deadline_status"
            ],
            alternative_deadline_status=alternative_constraints[
                "deadline_status"
            ],
            disruption_delay_minutes=disruption_delay
        )

        if comparison["propose"]:
            return {
                "decision": "PROPOSE",
                "reason": comparison["reason"],
                "confidence": confidence,
                "current_journey": current_journey,
                "current_constraints": current_constraints,
                "impact": impact,
                "disruption_delay_minutes": disruption_delay,
                "alternative": alternative_result,
                "alternative_constraints": alternative_constraints,
                "comparison": comparison,
                "confirmation_required": True
            }

        return {
            "decision": "KEEP",
            "reason": comparison["reason"],
            "confidence": confidence,
            "current_journey": current_journey,
            "current_constraints": current_constraints,
            "impact": impact,
            "disruption_delay_minutes": disruption_delay,
            "alternative": alternative_result,
            "alternative_constraints": alternative_constraints,
            "comparison": comparison,
            "confirmation_required": False
        }

    except Exception as e:

        return {
            "error": type(e).__name__,
            "message": str(e)
        }