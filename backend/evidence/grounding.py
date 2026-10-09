"""
Entity and Temporal Grounding Module for Mumbai Transit.
Validates extracted locations, routes, and timestamps against authoritative Mumbai reference data.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from backend.evidence.schemas import (
    ExtractedEvidence,
    GroundedEvidence,
    EntityGroundingStatus,
    TimeGroundingStatus
)


class MumbaiGroundingEngine:
    """Grounds transit entities and timestamps against Mumbai reference dataset."""

    def __init__(self, reference_path: Optional[str] = None):
        if reference_path is None:
            # Default to data/mumbai_reference.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            reference_path = os.path.join(base_dir, "data", "mumbai_reference.json")
        
        self.reference_path = reference_path
        self.routes_by_id: Dict[str, Any] = {}
        self.stops_by_id: Dict[str, Any] = {}
        self.alias_to_stop_id: Dict[str, str] = {}
        self.alias_to_route_id: Dict[str, str] = {}
        self.load_reference_data()

    def load_reference_data(self) -> None:
        """Loads and indexes Mumbai transit entities from JSON."""
        if not os.path.exists(self.reference_path):
            return

        with open(self.reference_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Index routes
        for route in data.get("routes", []):
            r_id = route["route_id"]
            self.routes_by_id[r_id] = route
            self.alias_to_route_id[r_id.lower()] = r_id
            self.alias_to_route_id[route.get("route_short_name", "").lower()] = r_id
            for alias in route.get("aliases", []):
                self.alias_to_route_id[alias.lower().strip()] = r_id

        # Index stops
        for stop in data.get("stops", []):
            s_id = stop["stop_id"]
            self.stops_by_id[s_id] = stop
            self.alias_to_stop_id[s_id.lower()] = s_id
            self.alias_to_stop_id[stop.get("stop_name", "").lower()] = s_id
            for alias in stop.get("aliases", []):
                self.alias_to_stop_id[alias.lower().strip()] = s_id

    def ground_entities(self, location_text: Optional[str], route_text: Optional[str], stop_text: Optional[str]) -> Tuple[EntityGroundingStatus, Optional[str], Optional[str], Optional[str], str]:
        """
        Grounds location, route, and stop against known Mumbai reference entities.
        Returns (EntityGroundingStatus, grounded_location, grounded_route_id, grounded_stop_id, notes).
        """
        matched_stop_id = None
        matched_route_id = None
        matched_location_name = None
        notes = []

        # Ground Stop/Location
        query_locs = [text for text in [stop_text, location_text] if text]
        for loc in query_locs:
            clean_loc = loc.lower().strip()
            # Direct match or alias match
            if clean_loc in self.alias_to_stop_id:
                matched_stop_id = self.alias_to_stop_id[clean_loc]
                matched_location_name = self.stops_by_id[matched_stop_id]["stop_name"]
                notes.append(f"Grounded stop '{loc}' -> {matched_stop_id}")
                break
            else:
                # Substring match
                for alias, s_id in self.alias_to_stop_id.items():
                    if alias in clean_loc or clean_loc in alias:
                        matched_stop_id = s_id
                        matched_location_name = self.stops_by_id[s_id]["stop_name"]
                        notes.append(f"Sub-matched stop '{loc}' -> {s_id}")
                        break
                if matched_stop_id:
                    break

        # Ground Route
        query_routes = [text for text in [route_text, location_text] if text]
        for r_query in query_routes:
            clean_r = r_query.lower().strip()
            if clean_r in self.alias_to_route_id:
                matched_route_id = self.alias_to_route_id[clean_r]
                notes.append(f"Grounded route '{r_query}' -> {matched_route_id}")
                break
            else:
                for alias, r_id in self.alias_to_route_id.items():
                    if alias in clean_r or clean_r in alias:
                        matched_route_id = r_id
                        notes.append(f"Sub-matched route '{r_query}' -> {r_id}")
                        break
                if matched_route_id:
                    break

        # If stop has associated route and route wasn't explicitly stated, infer if unique
        if matched_stop_id and not matched_route_id:
            associated_routes = self.stops_by_id[matched_stop_id].get("routes", [])
            if len(associated_routes) == 1:
                matched_route_id = associated_routes[0]
                notes.append(f"Inferred route {matched_route_id} from single-route stop {matched_stop_id}")

        # Determine overall entity grounding status
        if matched_stop_id or matched_route_id:
            status = EntityGroundingStatus.KNOWN
            if not matched_location_name and location_text:
                matched_location_name = location_text
        else:
            # If text was given but matched nothing in Mumbai
            if location_text or route_text or stop_text:
                status = EntityGroundingStatus.UNKNOWN
                notes.append("Entities present but not found in Mumbai reference database")
            else:
                status = EntityGroundingStatus.AMBIGUOUS
                notes.append("No location or route entities specified")

        return status, matched_location_name, matched_route_id, matched_stop_id, "; ".join(notes)

    def ground_time(
        self,
        report_timestamp: datetime,
        reference_now: Optional[datetime] = None,
        max_future_minutes: int = 15,
        max_past_hours: int = 48
    ) -> Tuple[TimeGroundingStatus, float, str]:
        """
        Validates evidence timestamp against temporal plausibility.
        Returns (TimeGroundingStatus, age_in_minutes, notes).
        """
        now = reference_now or datetime.now(timezone.utc)
        
        # Ensure timestamp has timezone awareness or match
        if report_timestamp.tzinfo is None and now.tzinfo is not None:
            # Treat naive as matching now's tz
            now = now.replace(tzinfo=None)
        elif report_timestamp.tzinfo is not None and now.tzinfo is None:
            report_timestamp = report_timestamp.replace(tzinfo=None)

        delta_seconds = (now - report_timestamp).total_seconds()
        age_minutes = delta_seconds / 60.0

        # Impossible future timestamp check
        if age_minutes < -max_future_minutes:
            return TimeGroundingStatus.UNGROUNDABLE, age_minutes, f"Impossible future timestamp ({age_minutes:.1f} mins in future)"

        # Grossly stale / out-of-bounds historical check
        if age_minutes > (max_past_hours * 60):
            return TimeGroundingStatus.UNGROUNDABLE, age_minutes, f"Excessively stale timestamp ({age_minutes/60.0:.1f} hours old)"

        return TimeGroundingStatus.GROUNDED, max(0.0, age_minutes), "Timestamp within valid temporal window"

    def ground_evidence(
        self,
        extracted: ExtractedEvidence,
        reference_now: Optional[datetime] = None
    ) -> GroundedEvidence:
        """Performs full entity and temporal grounding for an extracted item."""
        entity_status, grounded_loc, grounded_route, grounded_stop, entity_notes = self.ground_entities(
            location_text=extracted.location,
            route_text=extracted.route_id,
            stop_text=extracted.stop_id
        )

        time_status, age_mins, time_notes = self.ground_time(
            report_timestamp=extracted.timestamp,
            reference_now=reference_now
        )

        # Build notes
        all_notes = f"{entity_notes} | {time_notes}"

        return GroundedEvidence(
            extracted=extracted,
            entity_status=entity_status,
            time_status=time_status,
            grounded_location=grounded_loc or extracted.location,
            grounded_route_id=grounded_route or extracted.route_id,
            grounded_stop_id=grounded_stop or extracted.stop_id,
            grounding_notes=all_notes,
            event_time=extracted.timestamp,
            age_minutes=age_mins,
            freshness_weight=1.0  # Freshness engine calculates exact value
        )
