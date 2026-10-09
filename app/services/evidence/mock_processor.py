from typing import Dict, Any, Tuple
from datetime import datetime, timezone
from app.services.evidence.base import BaseEvidenceProcessor
from app.db.models import TrustStatusEnum, ValidationStatusEnum


class MockEvidenceProcessor(BaseEvidenceProcessor):
    """Deterministic mock evidence processor for Mumbai MVP."""

    def process_report(
        self,
        report_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        raw_text = report_data.get("raw_text", "").lower()
        source_type = report_data.get("source_type", "CROWD").upper()

        # Simple deterministic rule parsing
        if "flood" in raw_text or "waterlog" in raw_text:
            event_type = "FLOODING"
            title = "Waterlogging on Transit Corridor"
            severity = "HIGH"
            affected_line = "Metro Line 1"
            affected_stop = "Dadar Station"
            affected_route = "BEST Bus 351"
        elif "strike" in raw_text or "protest" in raw_text:
            event_type = "STRIKE"
            title = "Public Transport Drivers Strike"
            severity = "HIGH"
            affected_line = "BEST Bus Network"
            affected_stop = None
            affected_route = "BEST Bus 351"
        else:
            event_type = "DELAY"
            title = "Moderate Transit Congestion / Delay"
            severity = "MEDIUM"
            affected_line = "Metro Line 1"
            affected_stop = "Andheri Station"
            affected_route = "Metro Line 1"

        # Official sources automatically get CONFIRMED trust status
        if source_type == "OFFICIAL":
            trust_status = TrustStatusEnum.CONFIRMED
            confidence_score = 0.95
        else:
            trust_status = TrustStatusEnum.WATCH
            confidence_score = 0.70

        event_dict = {
            "event_type": event_type,
            "status": "ACTIVE",
            "trust_status": trust_status,
            "title": title,
            "description": report_data.get("raw_text"),
            "affected_line": affected_line,
            "affected_stop": affected_stop,
            "affected_route": affected_route,
            "severity": severity,
            "latitude": report_data.get("latitude", 19.0178),
            "longitude": report_data.get("longitude", 72.8478),
            "valid_from": datetime.now(timezone.utc),
            "confidence_score": confidence_score
        }

        evidence_dict = {
            "source_type": source_type,
            "source_name": report_data.get("source_name", "Crowd Reporter"),
            "location_match": 0.9,
            "time_match": 1.0,
            "evidence_weight": 0.85 if source_type == "OFFICIAL" else 0.60,
            "freshness_score": 1.0,
            "independence_group": report_data.get("source_name", "default"),
            "validation_status": ValidationStatusEnum.VALID
        }

        report_dict = {
            "source_type": source_type,
            "source_name": report_data.get("source_name", "Crowd Reporter"),
            "source_url": report_data.get("source_url"),
            "raw_text": report_data.get("raw_text"),
            "published_at": report_data.get("published_at") or datetime.now(timezone.utc),
            "retrieved_at": datetime.now(timezone.utc),
            "latitude": report_data.get("latitude"),
            "longitude": report_data.get("longitude"),
            "metadata": report_data.get("metadata", {})
        }

        return event_dict, evidence_dict, report_dict
