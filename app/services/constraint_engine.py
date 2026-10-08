from datetime import datetime, timedelta

from app.models.journey import Journey
from app.schemas.journey import JourneyRequest
from app.services.delay_model import calculate_delay


def check_constraints(
    journey: Journey,
    request: JourneyRequest
) -> dict:

    violations = []

    if (
        request.max_walking is not None
        and journey.walking_m > request.max_walking
    ):
        violations.append({
            "type": "MAX_WALKING",
            "message": (
                f"Walking distance {journey.walking_m}m "
                f"exceeds limit {request.max_walking}m"
            )
        })

    if (
        request.transfer_tolerance is not None
        and journey.transfers > request.transfer_tolerance
    ):
        violations.append({
            "type": "MAX_TRANSFERS",
            "message": (
                f"Transfers {journey.transfers} "
                f"exceed limit {request.transfer_tolerance}"
            )
        })

    if (
        request.budget is not None
        and journey.fare is not None
        and journey.fare > request.budget
    ):
        violations.append({
            "type": "BUDGET",
            "message": (
                f"Fare {journey.fare} "
                f"exceeds budget {request.budget}"
            )
        })

    if request.forbidden_modes:
        forbidden = {
            mode.upper()
            for mode in request.forbidden_modes
        }

        for leg in journey.legs:

            if leg.mode.upper() in forbidden:

                violations.append({
                    "type": "FORBIDDEN_MODE",
                    "message": (
                        f"Mode {leg.mode} is forbidden"
                    )
                })

    if request.accessibility_required:

        if not journey.wheelchair_accessible:

            violations.append({
                "type": "ACCESSIBILITY",
                "message": (
                    "Journey does not satisfy "
                    "accessibility requirements"
                )
            })

    deadline_status = None

    if request.deadline and journey.arrival:

        deadline = datetime.fromisoformat(
            request.deadline
        )

        scheduled_arrival = datetime.fromisoformat(
            journey.arrival
        )

        if deadline.tzinfo is None:

            deadline = deadline.replace(
                tzinfo=scheduled_arrival.tzinfo
            )

        delay = calculate_delay("MEDIUM")

        predicted_arrival = (
            scheduled_arrival
            + timedelta(minutes=delay)
        )

        remaining_minutes = (
            deadline - scheduled_arrival
        ).total_seconds() / 60

        if predicted_arrival > deadline:

            deadline_status = "INFEASIBLE"

            violations.append({
                "type": "DEADLINE",
                "message": (
                    "Predicted arrival exceeds "
                    "traveller deadline"
                )
            })

        elif remaining_minutes >= 15:

            deadline_status = "PROTECTED"

        else:

            deadline_status = "FEASIBLE"

    return {
        "feasible": len(violations) == 0,
        "deadline_status": deadline_status,
        "violations": violations
    }