
    
"""GTFS Schedule ingestion for local ZIP files and configurable feed URLs.

This module parses schedule data. It does not claim to measure live
passenger occupancy or validate whether a publisher is authoritative.
"""

import csv
import hashlib
import io
import os
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GTFSAdapter:
    REQUIRED_FILES = (
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    )

    def __init__(
        self,
        feed_url: str = "",
        feed_path: str = "",
        timeout_seconds: int = 30,
        provenance: str = "unverified",
    ) -> None:
        self.feed_url = feed_url or os.getenv("GTFS_FEED_URL", "")
        self.feed_path = feed_path or os.getenv("GTFS_FEED_PATH", "")
        self.timeout_seconds = timeout_seconds
        self.provenance = provenance
        self._zip_bytes: bytes | None = None
        self._tables: dict[str, list[dict[str, str]]] = {}
        self._metadata: dict[str, Any] = {}

    def _load(self) -> None:
        # Do not re-parse a feed or overwrite metadata after validation.
        if self._tables and self._metadata:
            return

        if self._zip_bytes is None:
            if self.feed_path:
                self._zip_bytes = Path(self.feed_path).read_bytes()
            elif self.feed_url:
                request = urllib.request.Request(
                    self.feed_url,
                    headers={"User-Agent": "TrustRoute-GTFS/1.0"},
                )
                with urllib.request.urlopen(
                    request, timeout=self.timeout_seconds
                ) as response:
                    self._zip_bytes = response.read()
            else:
                raise ValueError(
                    "Configure GTFS_FEED_PATH or GTFS_FEED_URL."
                )

        digest = hashlib.sha256(self._zip_bytes).hexdigest()

        try:
            with zipfile.ZipFile(io.BytesIO(self._zip_bytes)) as archive:
                # GTFS files can be at the ZIP root or inside a directory.
                names: dict[str, str] = {}
                for archive_name in archive.namelist():
                    normalized = archive_name.replace("\\", "/")
                    basename = normalized.split("/")[-1]
                    if basename.lower().endswith(".txt"):
                        names[basename] = archive_name

                missing = [
                    name for name in self.REQUIRED_FILES
                    if name not in names
                ]
                if missing:
                    raise ValueError(
                        f"GTFS feed is missing required files: {missing}"
                    )

                for filename, archive_name in names.items():
                    with archive.open(archive_name) as binary_file:
                        text_file = io.TextIOWrapper(
                            binary_file, encoding="utf-8-sig", newline=""
                        )
                        table_name = filename[:-4]
                        self._tables[table_name] = [
                            dict(row) for row in csv.DictReader(text_file)
                        ]

        except zipfile.BadZipFile as exc:
            raise ValueError("Feed is not a valid ZIP archive.") from exc

        self._metadata = {
            "source_url": self.feed_url or None,
            "source_path": self.feed_path or None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": digest,
            "provenance": self.provenance,
            "feed_info": (
                self._tables.get("feed_info", [{}])[0]
                if self._tables.get("feed_info")
                else None
            ),
            "validation_status": "loaded_pending_validation",
        }

    def _table(self, name: str) -> list[dict[str, str]]:
        self._load()
        return self._tables.get(name, [])

    def fetch_routes(self) -> list[dict[str, Any]]:
        return self._table("routes")

    def fetch_stops(self) -> list[dict[str, Any]]:
        return self._table("stops")

    def fetch_trips(self) -> list[dict[str, Any]]:
        return self._table("trips")

    def fetch_stop_times(self) -> list[dict[str, Any]]:
        return self._table("stop_times")

    def get_feed_metadata(self) -> dict[str, Any]:
        self._load()
        return dict(self._metadata)

    def validate(self) -> dict[str, Any]:
        """Run basic structural and foreign-key checks."""
        tables = {
            name: self._table(name)
            for name in ("routes", "stops", "trips", "stop_times")
        }
        errors: list[str] = []

        for name, field in (
            ("routes", "route_id"),
            ("stops", "stop_id"),
            ("trips", "trip_id"),
        ):
            ids = [row.get(field, "").strip() for row in tables[name]]
            if any(not value for value in ids):
                errors.append(f"{name}.txt contains blank {field}.")
            if len(ids) != len(set(ids)):
                errors.append(f"{name}.txt contains duplicate {field} values.")

        route_ids = {row.get("route_id") for row in tables["routes"]}
        stop_ids = {row.get("stop_id") for row in tables["stops"]}
        trip_ids = {row.get("trip_id") for row in tables["trips"]}

        for trip in tables["trips"]:
            if trip.get("route_id") not in route_ids:
                errors.append(
                    f"Trip {trip.get('trip_id')} references an unknown route."
                )
            if not trip.get("trip_id") or not trip.get("service_id"):
                errors.append("A trip has a missing trip_id or service_id.")

        for stop_time in tables["stop_times"]:
            if stop_time.get("trip_id") not in trip_ids:
                errors.append("A stop time references an unknown trip.")
            if stop_time.get("stop_id") not in stop_ids:
                errors.append("A stop time references an unknown stop.")

        self._metadata["validation_status"] = (
            "rejected" if errors else "basic_checks_passed"
        )
        self._metadata["validation_errors"] = errors

        return {
            "status": self._metadata["validation_status"],
            "errors": errors,
            "counts": {
                name: len(rows) for name, rows in tables.items()
            },
            "metadata": self.get_feed_metadata(),
        }

    @staticmethod
    def _seconds(value: str) -> int:
        """Convert GTFS HH:MM:SS to seconds; hours may exceed 23."""
        parts = value.strip().split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid GTFS time: {value!r}")

        try:
            hours, minutes, seconds = map(int, parts)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid GTFS time: {value!r}") from exc

        if (
            hours < 0
            or not 0 <= minutes < 60
            or not 0 <= seconds < 60
        ):
            raise ValueError(f"Invalid GTFS time: {value!r}")

        return hours * 3600 + minutes * 60 + seconds

    def get_departures_by_window(
        self,
        start_time: str = "08:00:00",
        end_time: str = "11:00:00",
    ) -> list[dict[str, Any]]:
        """Count scheduled departures by route in a half-open time window.

        Regular trips are counted from their first stop_time. Trips listed
        in frequencies.txt are counted from their frequency intervals
        instead, preventing the template trip from being double-counted.
        exact_times=1 produces schedule-based departures. Other values
        produce a fractional expected-service estimate.
        """
        start_seconds = self._seconds(start_time)
        end_seconds = self._seconds(end_time)

        if end_seconds <= start_seconds:
            raise ValueError("end_time must be later than start_time.")

        routes = {
            row["route_id"]: row for row in self._table("routes")
            if row.get("route_id")
        }
        trips = {
            row["trip_id"]: row for row in self._table("trips")
            if row.get("trip_id")
        }

        counts: dict[str, dict[str, Any]] = {}

        def bucket(route_id: str) -> dict[str, Any]:
            if route_id not in counts:
                route = routes.get(route_id, {})
                counts[route_id] = {
                    "route_id": route_id,
                    "route_name": (
                        route.get("route_long_name")
                        or route.get("route_short_name")
                        or route_id
                    ),
                    "scheduled_departures": 0,
                    "frequency_based_departures": 0,
                    "estimated_frequency_departures": 0.0,
                }
            return counts[route_id]

        frequencies = self._table("frequencies")
        frequency_trip_ids = {
            row.get("trip_id", "") for row in frequencies
            if row.get("trip_id")
        }

        # For ordinary trips, use the departure/arrival time at the
        # earliest stop_sequence.
        first_times: dict[str, tuple[int, int]] = {}

        for row in self._table("stop_times"):
            trip_id = row.get("trip_id", "")
            if not trip_id or trip_id in frequency_trip_ids:
                continue

            try:
                sequence = int(row["stop_sequence"])
                time_text = row.get("departure_time") or row.get("arrival_time") or ""
                seconds = self._seconds(time_text)
            except (KeyError, TypeError, ValueError):
                continue

            if (
                trip_id not in first_times
                or sequence < first_times[trip_id][0]
            ):
                first_times[trip_id] = (sequence, seconds)

        for trip_id, (_, seconds) in first_times.items():
            if start_seconds <= seconds < end_seconds:
                trip = trips.get(trip_id, {})
                route_id = trip.get("route_id")
                if route_id:
                    bucket(route_id)["scheduled_departures"] += 1

        # For frequency-based trips, count headway departures within the
        # overlap of the query window and [start_time, end_time).
        for row in frequencies:
            trip = trips.get(row.get("trip_id", ""))
            if not trip:
                continue

            route_id = trip.get("route_id")
            if not route_id:
                continue

            try:
                freq_start = self._seconds(row["start_time"])
                freq_end = self._seconds(row["end_time"])
                headway = int(row["headway_secs"])
            except (KeyError, TypeError, ValueError):
                continue

            if headway <= 0 or freq_end <= freq_start:
                continue

            overlap_start = max(start_seconds, freq_start)
            overlap_end = min(end_seconds, freq_end)
            if overlap_start >= overlap_end:
                continue

            result = bucket(route_id)
            exact_times = row.get("exact_times", "0")

            if exact_times == "1":
                first_k = max(
                    0,
                    (overlap_start - freq_start + headway - 1) // headway,
                )
                last_k = (overlap_end - 1 - freq_start) // headway
                departures = max(0, last_k - first_k + 1)

                result["scheduled_departures"] += departures
                result["frequency_based_departures"] += departures
            else:
                result["estimated_frequency_departures"] += (
                    (overlap_end - overlap_start) / headway
                )

        window_hours = (end_seconds - start_seconds) / 3600
        output: list[dict[str, Any]] = []

        for result in counts.values():
            total = (
                result["scheduled_departures"]
                + result["estimated_frequency_departures"]
            )
            result["estimated_frequency_departures"] = round(
                result["estimated_frequency_departures"], 2
            )
            result["departures_per_hour"] = round(total / window_hours, 2)
            result["passenger_crowding_measured"] = False
            output.append(result)

        return sorted(output, key=lambda item: item["route_id"])
