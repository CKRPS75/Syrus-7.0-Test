import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Float, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from sqlalchemy.ext.compiler import compiles
import enum

@compiles(Geometry, 'sqlite')
def compile_geometry_sqlite(type_, compiler, **kw):
    return "TEXT"


from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TrustStatusEnum(str, enum.Enum):
    IGNORE = "IGNORE"
    WATCH = "WATCH"
    CONFIRMED = "CONFIRMED"


class ValidationStatusEnum(str, enum.Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNGROUNDABLE = "UNGROUNDABLE"
    PENDING = "PENDING"


class ReplanStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class DecisionEnum(str, enum.Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class TravellerModel(Base):
    __tablename__ = "travellers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    budget: Mapped[float] = mapped_column(Float, default=100.0)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    max_walking_minutes: Mapped[int] = mapped_column(Integer, default=30)
    accessibility_required: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_tolerance: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 (cautious) to 1.0 (risk seeking)
    allowed_modes: Mapped[dict] = mapped_column(JSONB, default=lambda: ["BUS", "METRO", "WALK"])
    forbidden_modes: Mapped[dict] = mapped_column(JSONB, default=list)
    transfer_tolerance: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    journeys: Mapped[List["JourneyModel"]] = relationship("JourneyModel", back_populates="traveller", cascade="all, delete-orphan")


class JourneyModel(Base):
    __tablename__ = "journeys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    traveller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("travellers.id", ondelete="CASCADE"), nullable=False)
    origin: Mapped[dict] = mapped_column(JSONB, nullable=False)  # {"lat": float, "lng": float, "name": str}
    destination: Mapped[dict] = mapped_column(JSONB, nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")  # ACTIVE, COMPLETED, CANCELLED
    current_itinerary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="SET NULL", use_alter=True, name="fk_journey_current_itinerary"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    traveller: Mapped["TravellerModel"] = relationship("TravellerModel", back_populates="journeys")
    itineraries: Mapped[List["ItineraryModel"]] = relationship(
        "ItineraryModel", foreign_keys="ItineraryModel.journey_id", back_populates="journey", cascade="all, delete-orphan"
    )
    route_impacts: Mapped[List["RouteImpactModel"]] = relationship("RouteImpactModel", back_populates="journey", cascade="all, delete-orphan")
    replan_proposals: Mapped[List["ReplanProposalModel"]] = relationship("ReplanProposalModel", back_populates="journey", cascade="all, delete-orphan")


class ItineraryModel(Base):
    __tablename__ = "itineraries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    total_duration: Mapped[int] = mapped_column(Integer, nullable=False)  # in minutes
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_fare: Mapped[float] = mapped_column(Float, default=0.0)
    walking_minutes: Mapped[int] = mapped_column(Integer, default=0)
    transfers: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    is_protected: Mapped[bool] = mapped_column(Boolean, default=True)
    route_data: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Detailed legs, geometry, steps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    journey: Mapped["JourneyModel"] = relationship("JourneyModel", foreign_keys=[journey_id], back_populates="itineraries")


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # DISRUPTION, DELAY, ACCIDENT, FLOODING, STRIKE
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    trust_status: Mapped[TrustStatusEnum] = mapped_column(SQLEnum(TrustStatusEnum, name="truststatusenum"), default=TrustStatusEnum.WATCH)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    affected_line: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    affected_stop: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    affected_route: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=False), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    evidence_records: Mapped[List["EvidenceModel"]] = relationship("EvidenceModel", back_populates="event", cascade="all, delete-orphan")
    route_impacts: Mapped[List["RouteImpactModel"]] = relationship("RouteImpactModel", back_populates="event", cascade="all, delete-orphan")


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CROWD, OFFICIAL, NEWS, GDELT
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    evidence_records: Mapped[List["EvidenceModel"]] = relationship("EvidenceModel", back_populates="report", cascade="all, delete-orphan")


class EvidenceModel(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_match: Mapped[float] = mapped_column(Float, default=1.0)
    time_match: Mapped[float] = mapped_column(Float, default=1.0)
    evidence_weight: Mapped[float] = mapped_column(Float, default=1.0)
    freshness_score: Mapped[float] = mapped_column(Float, default=1.0)
    independence_group: Mapped[str] = mapped_column(String(100), default="default")
    validation_status: Mapped[ValidationStatusEnum] = mapped_column(
        SQLEnum(ValidationStatusEnum, name="validationstatusenum"), default=ValidationStatusEnum.VALID
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="evidence_records")
    report: Mapped["ReportModel"] = relationship("ReportModel", back_populates="evidence_records")


class RouteImpactModel(Base):
    __tablename__ = "route_impacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    journey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    affects_route: Mapped[bool] = mapped_column(Boolean, default=False)
    affected_leg: Mapped[dict] = mapped_column(JSONB, default=dict)
    estimated_delay: Mapped[int] = mapped_column(Integer, default=0)  # minutes
    route_feasible: Mapped[bool] = mapped_column(Boolean, default=True)
    route_protected: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="route_impacts")
    journey: Mapped["JourneyModel"] = relationship("JourneyModel", back_populates="route_impacts")


class ReplanProposalModel(Base):
    __tablename__ = "replan_proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    old_itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False)
    new_itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    time_saved: Mapped[int] = mapped_column(Integer, default=0)  # minutes
    status: Mapped[ReplanStatusEnum] = mapped_column(SQLEnum(ReplanStatusEnum, name="replanstatusenum"), default=ReplanStatusEnum.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    journey: Mapped["JourneyModel"] = relationship("JourneyModel", back_populates="replan_proposals")
    confirmations: Mapped[List["ConfirmationModel"]] = relationship("ConfirmationModel", back_populates="proposal", cascade="all, delete-orphan")


class ConfirmationModel(Base):
    __tablename__ = "confirmations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("replan_proposals.id", ondelete="CASCADE"), nullable=False)
    journey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    decision: Mapped[DecisionEnum] = mapped_column(SQLEnum(DecisionEnum, name="decisionenum"), nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    proposal: Mapped["ReplanProposalModel"] = relationship("ReplanProposalModel", back_populates="confirmations")


class DataSourceModel(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # GTFS, OSM, NEWS, CROWD
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    validation_status: Mapped[str] = mapped_column(String(50), default="VALID")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
