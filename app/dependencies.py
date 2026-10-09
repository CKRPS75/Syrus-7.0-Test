from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.mock_provider import MockRoutingProvider
from app.services.evidence.base import BaseEvidenceProcessor
from app.services.evidence.mock_processor import MockEvidenceProcessor
from app.services.journey_service import JourneyService
from app.services.event_service import EventService
from app.services.impact_service import ImpactService
from app.services.replan_service import ReplanService
from app.services.confirmation_service import ConfirmationService


def get_routing_provider() -> BaseRoutingProvider:
    return MockRoutingProvider()


def get_evidence_processor() -> BaseEvidenceProcessor:
    return MockEvidenceProcessor()


def get_journey_service(
    db: Session = Depends(get_db),
    routing_provider: BaseRoutingProvider = Depends(get_routing_provider)
) -> JourneyService:
    return JourneyService(db, routing_provider)


def get_event_service(
    db: Session = Depends(get_db),
    evidence_processor: BaseEvidenceProcessor = Depends(get_evidence_processor)
) -> EventService:
    return EventService(db, evidence_processor)


def get_impact_service(
    db: Session = Depends(get_db)
) -> ImpactService:
    return ImpactService(db)


def get_replan_service(
    db: Session = Depends(get_db),
    routing_provider: BaseRoutingProvider = Depends(get_routing_provider)
) -> ReplanService:
    return ReplanService(db, routing_provider)


def get_confirmation_service(
    db: Session = Depends(get_db)
) -> ConfirmationService:
    return ConfirmationService(db)
