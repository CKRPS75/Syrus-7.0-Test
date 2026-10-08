"""
TrustRoute Evidence & Trust Engine Schemas.
Defines Pydantic models for inputs, LLM extractions, grounding,
independence provenance, trust scoring, and the P3 event contract.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SourceType(str, Enum):
    OFFICIAL = "official"
    NEWS = "news"
    CROWD = "crowd"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class DisruptionType(str, Enum):
    DELAY = "DELAY"
    SUSPENSION = "SUSPENSION"
    CANCELLATION = "CANCELLATION"
    CLOSURE = "CLOSURE"
    ACCIDENT = "ACCIDENT"
    MAINTENANCE = "MAINTENANCE"
    CONGESTION = "CONGESTION"
    NORMAL_OPERATION = "NORMAL_OPERATION"
    UNKNOWN = "UNKNOWN"


class DisruptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class EntityGroundingStatus(str, Enum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    AMBIGUOUS = "AMBIGUOUS"


class TimeGroundingStatus(str, Enum):
    GROUNDED = "GROUNDED"
    UNGROUNDABLE = "UNGROUNDABLE"


class IndependenceType(str, Enum):
    INDEPENDENT = "independent"
    DUPLICATE = "duplicate"
    COPY_DERIVED = "copy-derived"
    UNKNOWN = "unknown"


class TrustDecision(str, Enum):
    IGNORE = "IGNORE"
    WATCH = "WATCH"
    CONFIRMED = "CONFIRMED"


class RawEvidenceInput(BaseModel):
    """Raw input payload received from external ingestion or /evidence/process."""
    source_id: str = Field(..., description="Unique identifier for the report/article/alert.")
    source_type: SourceType = Field(..., description="Source class: official, news, or crowd.")
    text: str = Field(..., min_length=1, description="Raw textual description of the disruption.")
    timestamp: datetime = Field(..., description="Report submission or publication timestamp.")
    author_id: Optional[str] = Field(None, description="Identifier for the reporting account or agency.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Auxiliary provenance info.")

    @field_validator("text")
    @classmethod
    def validate_non_empty_text(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Evidence text must not be empty.")
        return clean


class ExtractedEvidence(BaseModel):
    """Structured fields extracted from raw evidence by LLM or NLP extractor."""
    source_id: str
    source_type: SourceType
    raw_text: str
    location: Optional[str] = None
    route_id: Optional[str] = None
    stop_id: Optional[str] = None
    trip_id: Optional[str] = None
    disruption_type: DisruptionType = DisruptionType.UNKNOWN
    severity: Severity = Severity.UNKNOWN
    severity_inferred: bool = False
    timestamp: datetime
    status: DisruptionStatus = DisruptionStatus.ACTIVE
    description: Optional[str] = None


class GroundedEvidence(BaseModel):
    """Evidence item after entity and temporal grounding checks."""
    extracted: ExtractedEvidence
    entity_status: EntityGroundingStatus
    time_status: TimeGroundingStatus
    grounded_location: Optional[str] = None
    grounded_route_id: Optional[str] = None
    grounded_stop_id: Optional[str] = None
    grounding_notes: Optional[str] = None
    event_time: Optional[datetime] = None
    age_minutes: float = 0.0
    freshness_weight: float = 1.0


class EvidenceProvenance(BaseModel):
    """Provenance tracking for duplication, copy-rings, and independence."""
    evidence_id: str
    source_id: str
    source_type: SourceType
    author_id: Optional[str] = None
    independence: IndependenceType = IndependenceType.UNKNOWN
    parent_evidence_id: Optional[str] = None
    similarity_score: float = 0.0
    burst_detected: bool = False


class TrustScoreResult(BaseModel):
    """Trust calculation results for a single item or grouped disruption event."""
    prior_logit: float
    crowd_evidence_sum: float
    crowd_cap_applied: bool
    total_logit: float
    confidence_score: float  # P* uncalibrated confidence score
    decision: TrustDecision
    evidence_weights: Dict[str, float] = Field(default_factory=dict)
    contradiction_detected: bool = False
    official_override: bool = False


class DisruptionEvent(BaseModel):
    """
    Standardized Event Object for Person 3 (Impact Engine).
    Represents an evidence-weighted, grounded transit disruption.
    """
    event_id: str = Field(..., description="Unique event identifier (e.g., D01).")
    status: DisruptionStatus = Field(..., description="ACTIVE, RESOLVED, or EXPIRED.")
    decision: TrustDecision = Field(..., description="IGNORE, WATCH, or CONFIRMED.")
    
    location: Optional[str] = Field(None, description="Grounded location name.")
    route_id: Optional[str] = Field(None, description="Grounded route identifier (e.g., METRO_1).")
    stop_id: Optional[str] = Field(None, description="Grounded stop identifier (e.g., ANDHERI).")
    
    disruption_type: DisruptionType = Field(..., description="DELAY, CLOSURE, SUSPENSION, etc.")
    severity: Severity = Field(..., description="LOW, MEDIUM, HIGH, or UNKNOWN.")
    
    confidence_score: float = Field(..., description="Uncalibrated confidence score P* in [0, 1].")
    
    valid_from: datetime = Field(..., description="Start of validity window.")
    valid_until: Optional[datetime] = Field(None, description="End of validity window.")
    
    evidence_count: int = Field(..., description="Total evidence items grouped into this event.")
    independent_sources: int = Field(..., description="Number of distinct independent sources.")
    
    evidence_summary: List[str] = Field(default_factory=list, description="Human-readable provenance summary.")
    raw_evidence_ids: List[str] = Field(default_factory=list, description="IDs of linked evidence records.")


class ProcessEvidenceResponse(BaseModel):
    """Response returned by POST /evidence/process."""
    event_id: str
    status: TrustDecision
    lifecycle_status: DisruptionStatus
    confidence_score: float
    severity: Severity
    location: Optional[str] = None
    route_id: Optional[str] = None
    event: DisruptionEvent
