"""GTFS Data Ingestion Module Scaffold.
Future integration for Mumbai GTFS static feeds and real-time GTFS-RT updates.
"""
from typing import Dict, Any, List


class GTFSAdapter:
    def __init__(self, feed_url: str = ""):
        self.feed_url = feed_url

    def fetch_routes(self) -> List[Dict[str, Any]]:
        # TODO: Implement real GTFS route parsing
        return [{"route_id": "bus_351", "route_short_name": "351", "mode": "BUS"}]

    def fetch_stops(self) -> List[Dict[str, Any]]:
        # TODO: Implement real GTFS stop parsing
        return [{"stop_id": "andheri_01", "stop_name": "Andheri Metro Station"}]
