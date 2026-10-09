from datetime import timedelta


def should_propose_alternative(
    current_journey,
    alternative_journey,
    current_deadline_status=None,
    alternative_deadline_status=None,
    disruption_delay_minutes=0
):

    current_duration = sum(
        leg.duration_min or 0
        for leg in current_journey.legs
    )

    alternative_duration = sum(
        leg.duration_min or 0
        for leg in alternative_journey.legs
    )

    # Add expected disruption delay to current journey
    effective_current_duration = (
        current_duration
        + disruption_delay_minutes
    )

    time_saved = (
        effective_current_duration
        - alternative_duration
    )

    # Rule 1: 8+ minutes saved
    if time_saved >= 8:
        return {
            "propose": True,
            "reason": "Alternative saves at least 8 minutes after disruption delay",
            "time_saved_minutes": time_saved
        }

    # Rule 2: 15%+ improvement
    if effective_current_duration > 0:

        improvement = (
            time_saved
            / effective_current_duration
        ) * 100

        if improvement >= 15:
            return {
                "propose": True,
                "reason": "Alternative improves journey by at least 15%",
                "improvement_percent": round(
                    improvement,
                    2
                ),
                "time_saved_minutes": time_saved
            }

    # Rule 3: protected alternative
    if (
        current_deadline_status != "PROTECTED"
        and alternative_deadline_status == "PROTECTED"
    ):
        return {
            "propose": True,
            "reason": "Alternative provides a protected arrival",
            "time_saved_minutes": time_saved
        }

    return {
        "propose": False,
        "reason": "Alternative is not meaningfully better",
        "time_saved_minutes": time_saved
    }