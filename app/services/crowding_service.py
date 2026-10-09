from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EMPLOYMENT_DISTRICTS = {
    "bkc": "bkc",
    "bandra kurla complex": "bkc",
    "andheri": "andheri",
    "lower parel": "lower_parel",
    "lower parel station": "lower_parel",
    "south mumbai": "south_mumbai",
    "fort": "south_mumbai",
    "cst": "south_mumbai",
    "churchgate": "south_mumbai",
    "dadar": "dadar",
    "kurla": "kurla",
    "ghatkopar": "ghatkopar",
}


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = value.lower().replace(".", "").replace("station", "").replace("stn", "")
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned).strip()
    return cleaned


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = value.strip()
    for candidate in (text, text.replace("Z", "+00:00")):
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=None)
            return parsed
        except ValueError:
            continue
    return None


def _load_prior_dataset() -> dict[str, Any]:
    dataset_path = Path(__file__).resolve().parents[1] / "data" / "mumbai_crowd_priors.json"
    if dataset_path.exists():
        with dataset_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return data

    default_data = {
        "dataset_version": "demo-1.0",
        "city": "Mumbai",
        "source_status": "demo_prior_not_official_mmrda",
        "coverage": "Mumbai commuting corridors, including BKC, Andheri, Lower Parel, South Mumbai, Dadar, Kurla.",
        "entries": [
            {"correlation": "weekday_morning_inbound", "mode": "TRANSIT", "zone": "bkc", "direction": "inbound", "time_interval": "08:00-10:00", "prior": 0.78, "confidence": 0.64},
            {"correlation": "weekday_morning_inbound", "mode": "TRANSIT", "zone": "andheri", "direction": "inbound", "time_interval": "08:00-10:00", "prior": 0.71, "confidence": 0.62},
            {"correlation": "weekday_morning_inbound", "mode": "TRANSIT", "zone": "lower_parel", "direction": "inbound", "time_interval": "08:00-10:00", "prior": 0.74, "confidence": 0.63},
            {"correlation": "weekday_evening_outbound", "mode": "TRANSIT", "zone": "bkc", "direction": "outbound", "time_interval": "17:00-20:00", "prior": 0.68, "confidence": 0.61},
            {"correlation": "weekday_evening_outbound", "mode": "TRANSIT", "zone": "andheri", "direction": "outbound", "time_interval": "17:00-20:00", "prior": 0.67, "confidence": 0.6},
            {"correlation": "weekday_evening_outbound", "mode": "TRANSIT", "zone": "south_mumbai", "direction": "outbound", "time_interval": "17:00-20:00", "prior": 0.64, "confidence": 0.58},
            {"correlation": "weekday_offpeak", "mode": "TRANSIT", "zone": "all", "direction": "neutral", "time_interval": "10:00-16:00", "prior": 0.28, "confidence": 0.4},
        ],
    }
    return default_data


def _find_related_prior(destination: str, direction: str, time_bucket: str) -> float:
    dataset = _load_prior_dataset()
    destination_key = _normalize_text(destination)
    best_match = 0.35
    highest_confidence = 0.35

    for entry in dataset.get("entries", []):
        zone = _normalize_text(str(entry.get("zone", "")))
        if zone and zone in destination_key:
            if entry.get("direction") == direction and entry.get("time_interval") == time_bucket:
                value = float(entry.get("prior", 0.35))
                if value > best_match:
                    best_match = value
                    highest_confidence = float(entry.get("confidence", 0.35))
        elif zone == "all" and entry.get("direction") == direction:
            value = float(entry.get("prior", 0.35))
            if value > best_match:
                best_match = value
                highest_confidence = float(entry.get("confidence", 0.35))

    return best_match, highest_confidence


def estimate_crowding(
    origin: str | None,
    destination: str | None,
    departure_time: str | datetime | None,
    legs: list[Any] | None = None,
) -> dict[str, Any]:
    """Estimate a transparent, time-aware crowd-risk prior for a candidate route.

    The output is intentionally labelled as a historical prior / demo estimate and
    must not be interpreted as official passenger counts.
    """
    dt = _parse_datetime(departure_time)
    if dt is None:
        dt = datetime.utcnow()

    weekday = dt.weekday() < 5
    hour_float = dt.hour + dt.minute / 60.0
    destination_key = _normalize_text(destination)
    origin_key = _normalize_text(origin)

    morning_peak = weekday and 7.5 <= hour_float <= 10.5
    evening_peak = weekday and 17.0 <= hour_float <= 20.5
    offpeak = not morning_peak and not evening_peak

    risk = 0.2
    confidence = 0.35
    summary = "No strong commute signal identified; crowding remains low-confidence and should be treated as unknown for planning decisions."

    if destination_key:
        matched_district = next((name for name, token in EMPLOYMENT_DISTRICTS.items() if token in destination_key or destination_key in token), None)
        if matched_district:
            if morning_peak:
                risk += 0.35
                confidence += 0.22
                summary = (
                    f"Weekday morning commute toward {matched_district.upper()} suggests elevated inbound crowding risk on the supported corridors. "
                    "This is a historical prior, not an observed passenger count."
                )
            elif evening_peak:
                risk += 0.18
                confidence += 0.16
                summary = (
                    f"Weekday evening outbound crowding risk is elevated for {matched_district.upper()}-related travel. "
                    "The estimate is based on recurring habit patterns and service-supply context, not live occupancy data."
                )

    if origin_key:
        matched_origin = next((name for name, token in EMPLOYMENT_DISTRICTS.items() if token in origin_key or origin_key in token), None)
        if matched_origin and evening_peak:
            risk += 0.12
            confidence += 0.06

    if morning_peak and weekday and destination_key and "bkc" in destination_key:
        risk += 0.12
    if evening_peak and weekday and origin_key and "bkc" in origin_key:
        risk += 0.1

    if not weekday:
        risk *= 0.7
        confidence *= 0.75
        summary = "Weekend travel does not inherit the weekday commuter prior; risk is reduced unless another local signal is present."

    if legs:
        transit_legs = sum(1 for leg in legs if getattr(leg, "mode", "").upper() not in {"WALK", "BICYCLE"})
        if transit_legs:
            risk += min(0.18, 0.06 * transit_legs)
        if any(getattr(leg, "route_name", "") for leg in legs):
            risk += 0.02

    if offpeak:
        risk = min(risk, 0.45)
        summary = "Off-peak travel has no strong commute-pressure signal; crowding is treated as low-confidence and uncertain."

    prior_match, prior_conf = _find_related_prior(
        destination or origin or "mumbai",
        ("inbound" if morning_peak else "outbound" if evening_peak else "neutral"),
        "08:00-10:00" if morning_peak else "17:00-20:00" if evening_peak else "10:00-16:00",
    )
    risk = max(0.08, min(1.0, risk + prior_match * 0.15))
    confidence = max(0.2, min(0.9, confidence + prior_conf * 0.25))

    return {
        "crowding_risk": round(risk, 3),
        "confidence": round(confidence, 3),
        "evidence_sources": [
            "mumbai_crowd_priors_demo",
            "gtfs_service_supply_context",
        ],
        "evidence_timestamp": dt.isoformat(),
        "estimation_method": "transparent_demo_commute_prior",
        "data_quality": "inferred_demo_prior",
        "is_observed": False,
        "limitations": "This estimate reflects recurring time-of-week and corridor demand patterns only; it does not represent measured occupancy or an official MMRDA count.",
        "summary": summary,
    }
