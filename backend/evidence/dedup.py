"""
Event Deduplication Module.
Clusters incoming disruption reports into unified Disruption Events based on
spatial, route, disruption type, and temporal proximity.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from backend.evidence.schemas import GroundedEvidence, DisruptionStatus


class DisruptionCluster:
    """Represents an active cluster of evidence pointing to the same transit incident."""

    def __init__(self, event_id: str, primary_evidence: GroundedEvidence):
        self.event_id = event_id
        self.created_at = primary_evidence.extracted.timestamp
        self.last_updated_at = primary_evidence.extracted.timestamp
        self.route_id = primary_evidence.grounded_route_id
        self.stop_id = primary_evidence.grounded_stop_id
        self.location = primary_evidence.grounded_location
        self.disruption_type = primary_evidence.extracted.disruption_type
        self.severity = primary_evidence.extracted.severity
        self.status = primary_evidence.extracted.status or DisruptionStatus.ACTIVE
        self.evidence_items: List[GroundedEvidence] = [primary_evidence]

    def matches(self, item: GroundedEvidence, max_window_minutes: int = 60) -> bool:
        """
        Evaluates whether a new grounded evidence item belongs to this incident cluster.
        """
        # Time window check
        time_diff = abs((item.extracted.timestamp - self.last_updated_at).total_seconds()) / 60.0
        if time_diff > max_window_minutes:
            return False

        # Status check: If one is explicitly RESOLVED/NORMAL_OPERATION, they may cluster to resolve it
        # Spatial/Route check:
        route_match = (
            self.route_id is not None
            and item.grounded_route_id is not None
            and self.route_id == item.grounded_route_id
        )

        stop_match = (
            self.stop_id is not None
            and item.grounded_stop_id is not None
            and self.stop_id == item.grounded_stop_id
        )

        location_match = (
            self.location is not None
            and item.grounded_location is not None
            and (self.location.lower() in item.grounded_location.lower() or item.grounded_location.lower() in self.location.lower())
        )

        # Disruption clusters require:
        # 1. Matching stop/location (same station/area)
        # 2. OR matching route AND matching stop/location
        # 3. If one has stop and the other has a different distinct stop, they are separate incidents
        if self.stop_id and item.grounded_stop_id and self.stop_id != item.grounded_stop_id:
            return False

        if stop_match or location_match:
            return True

        if route_match and (not self.stop_id or not item.grounded_stop_id):
            return True

        return False

    def add_evidence(self, item: GroundedEvidence) -> None:
        """Adds evidence item and updates cluster metadata."""
        self.evidence_items.append(item)
        if item.extracted.timestamp > self.last_updated_at:
            self.last_updated_at = item.extracted.timestamp
        
        # Upgrade route or stop info if item has more specific grounding
        if not self.route_id and item.grounded_route_id:
            self.route_id = item.grounded_route_id
        if not self.stop_id and item.grounded_stop_id:
            self.stop_id = item.grounded_stop_id
        if not self.location and item.grounded_location:
            self.location = item.grounded_location


class DeduplicationEngine:
    """Manages active disruption clusters and assigns event IDs to incoming evidence."""

    def __init__(self, dedup_window_minutes: int = 60):
        self.dedup_window_minutes = dedup_window_minutes
        self.clusters: Dict[str, DisruptionCluster] = {}
        self._next_event_number = 1

    def _generate_event_id(self) -> str:
        eid = f"D{self._next_event_number:02d}"
        self._next_event_number += 1
        return eid

    def assign_event(self, item: GroundedEvidence) -> Tuple[str, DisruptionCluster, bool]:
        """
        Finds an existing matching cluster or creates a new one.
        Returns (event_id, cluster, is_new_event).
        """
        for event_id, cluster in self.clusters.items():
            if cluster.matches(item, max_window_minutes=self.dedup_window_minutes):
                cluster.add_evidence(item)
                return event_id, cluster, False

        # Create new cluster
        new_event_id = self._generate_event_id()
        new_cluster = DisruptionCluster(new_event_id, item)
        self.clusters[new_event_id] = new_cluster
        return new_event_id, new_cluster, True

    def get_cluster(self, event_id: str) -> Optional[DisruptionCluster]:
        return self.clusters.get(event_id)

    def reset(self) -> None:
        self.clusters.clear()
        self._next_event_number = 1
