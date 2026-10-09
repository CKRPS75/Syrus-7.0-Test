from app.models.journey import Journey, JourneyLeg
from app.models.disruption import Disruption
from app.services.impact_engine import check_impact


journey = Journey(
    journey_id="OTP-001",
    origin="Mumbai",
    destination="Bandra",
    departure="2026-10-08T18:00:00",
    arrival="2026-10-08T18:36:29+05:30",
    walking_m=1105,
    transfers=1,
    legs=[
        JourneyLeg(
            mode="WALK",
            from_place="Origin",
            to_place="Five Gardens",
            distance_m=940,
            duration_min=12
        ),
        JourneyLeg(
            mode="BUS",
            from_place="Five Gardens",
            to_place="Antop Hill",
            distance_m=1912,
            duration_min=3,
            route_name="15"
        ),
        JourneyLeg(
            mode="BUS",
            from_place="Antop Hill",
            to_place="Kurla Depot",
            distance_m=9302,
            duration_min=15,
            route_name="341AS"
        )
    ]
)

disruption = Disruption(
    disruption_id="D001",
    route_name="341AS",
    disruption_type="SERVICE_SUSPENSION",
    severity="HIGH",
    confirmed=True,
    active=True
)

result = check_impact(journey, disruption)

print(result)