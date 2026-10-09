
import csv
import io
import zipfile

import pytest

from ingestion.gtfs.adapter import GTFSAdapter


def create_gtfs_zip(path, *, include_required_files=True):
    """Create a tiny deterministic GTFS fixture for tests."""
    tables = {
        "routes.txt": [
            {"route_id": "R1", "route_short_name": "Line 1"},
        ],
        "stops.txt": [
            {"stop_id": "S1", "stop_name": "Start"},
            {"stop_id": "S2", "stop_name": "End"},
        ],
        "trips.txt": [
            {"route_id": "R1", "service_id": "DAILY", "trip_id": "T1"},
            {"route_id": "R1", "service_id": "DAILY", "trip_id": "T2"},
            {"route_id": "R1", "service_id": "DAILY", "trip_id": "T3"},
        ],
        "stop_times.txt": [
            {
                "trip_id": "T1",
                "arrival_time": "08:00:00",
                "departure_time": "08:00:00",
                "stop_id": "S1",
                "stop_sequence": "1",
            },
            {
                "trip_id": "T1",
                "arrival_time": "08:20:00",
                "departure_time": "08:20:00",
                "stop_id": "S2",
                "stop_sequence": "2",
            },
            {
                "trip_id": "T2",
                "arrival_time": "08:30:00",
                "departure_time": "08:30:00",
                "stop_id": "S1",
                "stop_sequence": "1",
            },
            {
                "trip_id": "T2",
                "arrival_time": "08:50:00",
                "departure_time": "08:50:00",
                "stop_id": "S2",
                "stop_sequence": "2",
            },
            {
                "trip_id": "T3",
                "arrival_time": "09:00:00",
                "departure_time": "09:00:00",
                "stop_id": "S1",
                "stop_sequence": "1",
            },
        ],
    }

    with zipfile.ZipFile(path, "w") as archive:
        selected = (
            tables
            if include_required_files
            else {"routes.txt": tables["routes.txt"]}
        )

        for filename, rows in selected.items():
            buffer = io.StringIO()
            writer = csv.DictWriter(
                buffer, fieldnames=list(rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(rows)
            archive.writestr(filename, buffer.getvalue())


def test_parses_routes_and_stops(tmp_path):
    path = tmp_path / "valid.zip"
    create_gtfs_zip(path)

    adapter = GTFSAdapter(
        feed_path=str(path),
        provenance="test_fixture",
    )

    assert adapter.fetch_routes()[0]["route_id"] == "R1"
    assert adapter.fetch_stops()[0]["stop_id"] == "S1"


def test_validation_passes_for_valid_fixture(tmp_path):
    path = tmp_path / "valid.zip"
    create_gtfs_zip(path)

    result = GTFSAdapter(feed_path=str(path)).validate()

    assert result["status"] == "basic_checks_passed"
    assert result["errors"] == []
    assert result["counts"]["trips"] == 3


def test_rejects_zip_missing_required_files(tmp_path):
    path = tmp_path / "incomplete.zip"
    create_gtfs_zip(path, include_required_files=False)

    adapter = GTFSAdapter(feed_path=str(path))

    with pytest.raises(ValueError, match="missing required files"):
        adapter.validate()


def test_rejects_invalid_zip(tmp_path):
    path = tmp_path / "invalid.zip"
    path.write_text("not a zip file")

    adapter = GTFSAdapter(feed_path=str(path))

    with pytest.raises(ValueError, match="valid ZIP"):
        adapter.validate()


def test_counts_departures_in_time_window(tmp_path):
    path = tmp_path / "valid.zip"
    create_gtfs_zip(path)

    adapter = GTFSAdapter(feed_path=str(path))
    result = adapter.get_departures_by_window(
        "08:00:00", "09:00:00"
    )

    assert len(result) == 1
    assert result[0]["route_id"] == "R1"
    assert result[0]["scheduled_departures"] == 2
    assert result[0]["departures_per_hour"] == 2.0
    assert result[0]["passenger_crowding_measured"] is False


def test_validation_status_is_preserved(tmp_path):
    path = tmp_path / "valid.zip"
    create_gtfs_zip(path)

    adapter = GTFSAdapter(feed_path=str(path))
    adapter.validate()

    metadata = adapter.get_feed_metadata()

    assert metadata["validation_status"] == "basic_checks_passed"


def test_reads_optional_frequencies_table(tmp_path):
    path = tmp_path / "frequencies.zip"
    create_gtfs_zip(path)

    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr(
            "frequencies.txt",
            "trip_id,start_time,end_time,headway_secs,exact_times\n"
            "T1,08:00:00,09:00:00,600,1\n",
        )

    adapter = GTFSAdapter(feed_path=str(path))

    assert adapter._table("frequencies") == [
        {
            "trip_id": "T1",
            "start_time": "08:00:00",
            "end_time": "09:00:00",
            "headway_secs": "600",
            "exact_times": "1",
        }
    ]


def test_feed_without_frequencies_still_works(tmp_path):
    path = tmp_path / "without-frequencies.zip"
    create_gtfs_zip(path)

    adapter = GTFSAdapter(feed_path=str(path))

    assert adapter._table("frequencies") == []
    assert adapter.validate()["status"] == "basic_checks_passed"


def test_frequency_trips_are_not_double_counted(tmp_path):
    path = tmp_path / "frequency_count.zip"
    create_gtfs_zip(path)

    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr(
            "frequencies.txt",
            "trip_id,start_time,end_time,headway_secs,exact_times\n"
            "T1,08:00:00,09:00:00,600,1\n",
        )

    adapter = GTFSAdapter(feed_path=str(path))
    result = adapter.get_departures_by_window(
        start_time="08:00:00",
        end_time="09:00:00",
    )

    route = next(
        item for item in result if item["route_id"] == "R1"
    )

    # T1: six departures every 10 minutes.
    # T2: one regular departure at 08:30.
    # T3: departure at 09:00 is outside the window.
    assert route["scheduled_departures"] == 7
