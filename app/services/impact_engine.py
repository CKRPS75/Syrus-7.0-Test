from app.models.journey import Journey
from app.models.disruption import Disruption


def check_impact(
    journey: Journey,
    disruption: Disruption
) -> dict:

    affected_legs = []

    for leg in journey.legs:

        route_affected = False
        stop_affected = False

        # Check route disruption
        if (
            disruption.route_name
            and leg.route_name
            and disruption.route_name.upper()
            == leg.route_name.upper()
        ):
            route_affected = True

        # Check stop disruption
        if disruption.stop_name:

            disrupted_stop = disruption.stop_name.upper()

            from_stop = (
                leg.from_place.upper()
                if leg.from_place
                else ""
            )

            to_stop = (
                leg.to_place.upper()
                if leg.to_place
                else ""
            )

            if (
                disrupted_stop in from_stop
                or disrupted_stop in to_stop
            ):
                stop_affected = True

        # Add affected leg
        if route_affected or stop_affected:

            impact_type = []

            if route_affected:
                impact_type.append(
                    "ROUTE_DISRUPTION"
                )

            if stop_affected:
                impact_type.append(
                    "STOP_DISRUPTION"
                )

            affected_legs.append({
                "mode": leg.mode,
                "route_name": leg.route_name,
                "from": leg.from_place,
                "to": leg.to_place,
                "impact": impact_type
            })

    return {
        "affected": len(affected_legs) > 0,
        "affected_legs": affected_legs
    }