"""
Seed script to populate initial development mock data for TrustRoute.
NOTE: This dataset contains synthetic demo data for local development and testing.
"""
import uuid
from datetime import datetime, timedelta, timezone
from app.db.database import SessionLocal, engine, Base
from app.db.models import (
    TravellerModel, JourneyModel, ItineraryModel, EventModel,
    ReportModel, EvidenceModel, RouteImpactModel, ReplanProposalModel,
    TrustStatusEnum, ValidationStatusEnum, ReplanStatusEnum
)


def seed_data():
    print("Seeding development database...")
    db = SessionLocal()

    try:
        # 1. Create Sample Traveller
        traveller_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        traveller = db.query(TravellerModel).filter(TravellerModel.id == traveller_id).first()
        if not traveller:
            traveller = TravellerModel(
                id=traveller_id,
                name="Aarav Sharma (Demo)",
                budget=150.0,
                deadline=datetime.now(timezone.utc) + timedelta(hours=2),
                max_walking_minutes=20,
                accessibility_required=False,
                risk_tolerance=0.2,  # Low risk tolerance (cautious)
                allowed_modes=["BUS", "METRO", "WALK"],
                forbidden_modes=[],
                transfer_tolerance=2
            )
            db.add(traveller)
            db.commit()

        # 2. Create Sample Journey
        journey_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
        journey = db.query(JourneyModel).filter(JourneyModel.id == journey_id).first()
        if not journey:
            journey = JourneyModel(
                id=journey_id,
                traveller_id=traveller.id,
                origin={"name": "Andheri West", "latitude": 19.1197, "longitude": 72.8464},
                destination={"name": "BKC Metro Station", "latitude": 19.0674, "longitude": 72.8686},
                departure_time=datetime.now(timezone.utc),
                status="ACTIVE"
            )
            db.add(journey)
            db.commit()

        # 3. Create Sample Initial Itinerary
        itinerary_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
        itinerary = db.query(ItineraryModel).filter(ItineraryModel.id == itinerary_id).first()
        if not itinerary:
            itinerary = ItineraryModel(
                id=itinerary_id,
                journey_id=journey.id,
                total_duration=45,
                arrival_time=datetime.now(timezone.utc) + timedelta(minutes=45),
                total_fare=30.0,
                walking_minutes=8,
                transfers=1,
                risk_score=0.1,
                is_current=True,
                is_protected=True,
                route_data={
                    "summary": "Walk -> BEST Bus 351 -> Metro Line 1 -> Walk",
                    "legs": [
                        {
                            "leg_id": "leg_1",
                            "mode": "WALK",
                            "from_name": "Andheri West",
                            "to_name": "Bus Stop",
                            "duration_minutes": 3,
                            "distance_km": 0.2
                        },
                        {
                            "leg_id": "leg_2",
                            "mode": "BUS",
                            "route_number": "BEST Bus 351",
                            "from_name": "Andheri West Depot",
                            "to_name": "Ghatkopar Station",
                            "duration_minutes": 25,
                            "distance_km": 8.5
                        },
                        {
                            "leg_id": "leg_3",
                            "mode": "METRO",
                            "line": "Metro Line 1",
                            "from_name": "Ghatkopar Station",
                            "to_name": "BKC Station",
                            "duration_minutes": 12,
                            "distance_km": 5.1
                        },
                        {
                            "leg_id": "leg_4",
                            "mode": "WALK",
                            "from_name": "BKC Station",
                            "to_name": "BKC Office Complex",
                            "duration_minutes": 5,
                            "distance_km": 0.4
                        }
                    ]
                }
            )
            db.add(itinerary)
            db.commit()

            journey.current_itinerary_id = itinerary.id
            db.commit()

        # 4. Create Sample Report
        report_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
        report = db.query(ReportModel).filter(ReportModel.id == report_id).first()
        if not report:
            report = ReportModel(
                id=report_id,
                source_type="CROWD",
                source_name="Twitter / Mumbai Traffic Alert",
                raw_text="Severe waterlogging on BEST Bus 351 route near Ghatkopar flyover. Bus operations delayed by 30+ minutes.",
                published_at=datetime.now(timezone.utc),
                retrieved_at=datetime.now(timezone.utc),
                latitude=19.0860,
                longitude=72.9081,
                metadata_={"hashtags": ["#MumbaiRains", "#GhatkoparTraffic"]}
            )
            db.add(report)
            db.commit()

        # 5. Create Sample Event
        event_id = uuid.UUID("55555555-5555-5555-5555-555555555555")
        event = db.query(EventModel).filter(EventModel.id == event_id).first()
        if not event:
            event = EventModel(
                id=event_id,
                event_type="FLOODING",
                status="ACTIVE",
                trust_status=TrustStatusEnum.CONFIRMED,
                title="Heavy Monsoon Flooding on Ghatkopar Bus Corridor",
                description="Severe waterlogging disrupting BEST Bus 351 services.",
                affected_line=None,
                affected_stop="Ghatkopar Station",
                affected_route="BEST Bus 351",
                severity="HIGH",
                latitude=19.0860,
                longitude=72.9081,
                valid_from=datetime.now(timezone.utc),
                confidence_score=0.92
            )
            db.add(event)
            db.commit()

        # 6. Create Sample Evidence
        evidence_id = uuid.UUID("66666666-6666-6666-6666-666666666666")
        evidence = db.query(EvidenceModel).filter(EvidenceModel.id == evidence_id).first()
        if not evidence:
            evidence = EvidenceModel(
                id=evidence_id,
                event_id=event.id,
                report_id=report.id,
                source_type="CROWD",
                source_name="Twitter / Mumbai Traffic Alert",
                location_match=0.95,
                time_match=1.0,
                evidence_weight=0.88,
                freshness_score=0.98,
                independence_group="crowd_twitter",
                validation_status=ValidationStatusEnum.VALID
            )
            db.add(evidence)
            db.commit()

        # 7. Create Sample Route Impact
        impact_id = uuid.UUID("77777777-7777-7777-7777-777777777777")
        impact = db.query(RouteImpactModel).filter(RouteImpactModel.id == impact_id).first()
        if not impact:
            impact = RouteImpactModel(
                id=impact_id,
                event_id=event.id,
                journey_id=journey.id,
                affects_route=True,
                affected_leg={
                    "leg_id": "leg_2",
                    "mode": "BUS",
                    "route_number": "BEST Bus 351"
                },
                estimated_delay=35,
                route_feasible=True,   # Physical alternative exists
                route_protected=False  # Violates cautious traveller risk tolerance / deadline
            )
            db.add(impact)
            db.commit()

        # 8. Create Sample Replan Proposal
        alt_itinerary_id = uuid.UUID("88888888-8888-8888-8888-888888888888")
        alt_itinerary = db.query(ItineraryModel).filter(ItineraryModel.id == alt_itinerary_id).first()
        if not alt_itinerary:
            alt_itinerary = ItineraryModel(
                id=alt_itinerary_id,
                journey_id=journey.id,
                total_duration=38,
                arrival_time=datetime.now(timezone.utc) + timedelta(minutes=38),
                total_fare=40.0,
                walking_minutes=6,
                transfers=1,
                risk_score=0.02,
                is_current=False,
                is_protected=True,
                route_data={
                    "summary": "Walk -> Metro Line 2A / 7 Direct -> Walk",
                    "reason": "Bypasses flooded bus corridor",
                    "legs": [
                        {
                            "leg_id": "alt_1",
                            "mode": "WALK",
                            "from_name": "Andheri West",
                            "to_name": "DN Nagar Metro",
                            "duration_minutes": 4,
                            "distance_km": 0.3
                        },
                        {
                            "leg_id": "alt_2",
                            "mode": "METRO",
                            "line": "Metro Line 2A / Line 7",
                            "from_name": "DN Nagar Metro",
                            "to_name": "BKC Metro Station",
                            "duration_minutes": 30,
                            "distance_km": 13.5
                        },
                        {
                            "leg_id": "alt_3",
                            "mode": "WALK",
                            "from_name": "BKC Metro Station",
                            "to_name": "BKC Office Complex",
                            "duration_minutes": 4,
                            "distance_km": 0.3
                        }
                    ]
                }
            )
            db.add(alt_itinerary)
            db.commit()

        proposal_id = uuid.UUID("99999999-9999-9999-9999-999999999999")
        proposal = db.query(ReplanProposalModel).filter(ReplanProposalModel.id == proposal_id).first()
        if not proposal:
            proposal = ReplanProposalModel(
                id=proposal_id,
                journey_id=journey.id,
                event_id=event.id,
                old_itinerary_id=itinerary.id,
                new_itinerary_id=alt_itinerary.id,
                reason="Severe bus corridor waterlogging detected. Switched to Metro Line 2A / 7 bypass.",
                time_saved=42,  # (45 + 35) - 38 = 42 minutes saved!
                status=ReplanStatusEnum.PENDING,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
            )
            db.add(proposal)
            db.commit()

        print("Seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
