from app.services.otp_service import plan_journey


def generate_alternative(journey, disruption):

    departure = journey.departure

    # OTP expects HH:MM:SS without timezone
    if "+" in departure:
        departure = departure.split("+")[0]

    candidates = plan_journey(
        origin=journey.origin,
        destination=journey.destination,
        departure=departure
    )

    valid_alternatives = []

    for candidate in candidates:

        uses_disrupted_route = False

        for leg in candidate.legs:

            if (
                leg.route_name
                and disruption.route_name
                and leg.route_name.upper()
                == disruption.route_name.upper()
            ):
                uses_disrupted_route = True
                break

        if not uses_disrupted_route:
            valid_alternatives.append(candidate)

    if not valid_alternatives:

        return {
            "alternative_found": False,
            "reason": (
                f"No alternative found that avoids "
                f"route {disruption.route_name}"
            ),
            "alternatives": []
        }

    best_alternative = min(
        valid_alternatives,
        key=lambda candidate: (
            candidate.arrival or "",
            candidate.transfers,
            candidate.walking_m,
            getattr(candidate, "crowding_risk", 1.0),
        )
    )

    return {
        "alternative_found": True,
        "reason": (
            f"Alternative avoids disrupted route "
            f"{disruption.route_name}"
        ),
        "journey": best_alternative,
        "alternatives_checked": len(candidates),
        "valid_alternatives": len(valid_alternatives)
    }