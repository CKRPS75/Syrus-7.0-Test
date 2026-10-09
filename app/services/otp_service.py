import json
import os
import requests

from app.models.journey import Journey, JourneyLeg
from app.services.crowding_service import estimate_crowding

OTP_URL = "http://localhost:8080/otp/routers/default/index/graphql"

# Cache reference coordinates for station/location lookup
_COORDINATES_MAP: dict[str, tuple[float, float]] = {}


def _get_coordinates_map() -> dict[str, tuple[float, float]]:
    global _COORDINATES_MAP
    if not _COORDINATES_MAP:
        # Defaults
        coords = {
            "dadar": (19.0178, 72.8478),
            "kurla": (19.0657, 72.8794),
            "andheri": (19.1197, 72.8464),
            "ghatkopar": (19.0860, 72.9090),
            "versova": (19.1378, 72.8135),
            "bandra": (19.0544, 72.8402),
            "bkc": (19.0660, 72.8687),
            "borivali": (19.2290, 72.8574),
            "churchgate": (18.9322, 72.8264),
            "csmt": (18.9401, 72.8354),
            "thane": (19.1860, 72.9759),
            "gundavali": (19.1171, 72.8561),
            "dn nagar": (19.1256, 72.8290),
            "d.n. nagar": (19.1256, 72.8290),
            "dahisar east": (19.2558, 72.8683),
        }

        # Attempt reading data/mumbai_reference.json for comprehensive aliases
        ref_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "mumbai_reference.json"
        )
        if os.path.exists(ref_path):
            try:
                with open(ref_path, "r", encoding="utf-8") as f:
                    ref_data = json.load(f)
                for stop in ref_data.get("stops", []):
                    lat = stop.get("latitude")
                    lon = stop.get("longitude")
                    if lat and lon:
                        coords[stop.get("stop_id", "").lower()] = (lat, lon)
                        coords[stop.get("stop_name", "").lower()] = (lat, lon)
                        for alias in stop.get("aliases", []):
                            coords[alias.lower()] = (lat, lon)
            except Exception:
                pass

        _COORDINATES_MAP = coords
    return _COORDINATES_MAP


def resolve_coordinates(location_name: str, fallback_lat: float, fallback_lon: float) -> tuple[float, float]:
    """
    Resolve coordinates for a given location or stop name.
    Falls back to given lat/lon if name not found.
    """
    if not location_name:
        return fallback_lat, fallback_lon

    key = location_name.strip().lower()
    coord_map = _get_coordinates_map()
    if key in coord_map:
        return coord_map[key]

    # Partial / substring match
    for alias, (lat, lon) in coord_map.items():
        if alias in key or key in alias:
            return lat, lon

    return fallback_lat, fallback_lon


def calculate_demo_fare(legs):
    """
    Synthetic demo fare for the project (clearly labelled demo estimate).

    This is NOT a real Mumbai transport fare.
    It is used because the current OTP query does not return
    fare information from the loaded demo GTFS.
    """

    transit_legs = [
        leg for leg in legs
        if leg["mode"].upper() not in {"WALK", "BICYCLE"}
    ]

    if not transit_legs:
        return 0.0

    # Demo assumption:
    # ₹20 for the first transit leg
    # ₹10 for every additional transit leg
    fare = 20 + (len(transit_legs) - 1) * 10

    return float(fare)


def _resolved_place_name(
    name: str | None,
    fallback: str,
    *,
    endpoint: str
) -> str:
    label = (name or "").strip()
    generic_labels = {
        "origin": {"origin", "start", "from"},
        "destination": {"destination", "end", "to"},
    }
    if endpoint in generic_labels and label.casefold() in generic_labels[endpoint]:
        return fallback
    return label or fallback


def _leg_sequence_signature(legs: list[JourneyLeg]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        (
            leg.mode.casefold(),
            (leg.route_name or "").casefold(),
            (leg.route_long_name or "").casefold(),
            leg.from_place.casefold(),
            leg.to_place.casefold(),
        )
        for leg in legs
    )


def plan_journey(
    origin: str,
    destination: str,
    departure: str,
    allowed_modes: list[str] | None = None
) -> list[Journey]:

    otp_modes = {
        "BUS": "BUS",
        "METRO": "SUBWAY",
        "TRAIN": "RAIL",
        "WALK": "WALK",
    }
    selected_modes = allowed_modes if allowed_modes is not None else list(otp_modes)
    transport_modes = ", ".join(
        f"{{ mode: {otp_modes[mode]} }}" for mode in selected_modes
    )
    if not selected_modes:
        return []

    query = """
    query TestJourney(
      $fromLat: Float!,
      $fromLon: Float!,
      $toLat: Float!,
      $toLon: Float!,
      $date: String!,
      $time: String!
    ) {
      plan(
        from: {
          lat: $fromLat
          lon: $fromLon
        }
        to: {
          lat: $toLat
          lon: $toLon
        }
        date: $date
        time: $time
        arriveBy: false
        transportModes: [__TRANSPORT_MODES__]
        numItineraries: 3
      ) {
        itineraries {
          start
          end
          duration
          walkDistance
          numberOfTransfers

          legs {
            mode

            start {
              scheduledTime
            }

            end {
              scheduledTime
            }

            duration
            distance

            from {
              name
              lat
              lon
            }

            to {
              name
              lat
              lon
            }

            route {
              shortName
              longName
            }
          }
        }

        routingErrors {
          code
          description
        }
      }
    }
    """
    query = query.replace("__TRANSPORT_MODES__", transport_modes)

    # Resolve coordinates dynamically from reference data, defaulting to Dadar and Kurla
    from_lat, from_lon = resolve_coordinates(origin, fallback_lat=19.0178, fallback_lon=72.8478)
    to_lat, to_lon = resolve_coordinates(destination, fallback_lat=19.0760, fallback_lon=72.8777)

    variables = {
        "fromLat": from_lat,
        "fromLon": from_lon,
        "toLat": to_lat,
        "toLon": to_lon,
        "date": departure.split("T")[0],
        "time": departure.split("T")[1],
    }

    response = requests.post(
        OTP_URL,
        json={
            "query": query,
            "variables": variables
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    plan = data["data"]["plan"]
    itineraries = plan["itineraries"]

    if not itineraries:
        raise Exception("OTP returned no itineraries")

    journeys_by_signature: dict[tuple[tuple[str, ...], ...], Journey] = {}

    for itinerary in itineraries:

        legs = []

        itinerary_legs = itinerary["legs"]
        for leg_index, leg in enumerate(itinerary_legs):

            route = leg.get("route") or {}

            from_name = leg["from"].get("name")
            to_name = leg["to"].get("name")
            if leg_index == 0:
                from_name = _resolved_place_name(
                    from_name,
                    origin,
                    endpoint="origin"
                )
            if leg_index == len(itinerary_legs) - 1:
                to_name = _resolved_place_name(
                    to_name,
                    destination,
                    endpoint="destination"
                )

            # Preserves actual transport mode (WALK, BUS, RAIL, SUBWAY) returned by OTP
            leg_mode = leg["mode"]

            legs.append(
                JourneyLeg(
                    mode=leg_mode,
                    from_place=from_name or origin,
                    to_place=to_name or destination,
                    distance_m=round(leg["distance"]),
                    duration_min=round(
                        leg["duration"] / 60
                    ),
                    route_name=route.get("shortName") or route.get("longName"),
                    route_long_name=route.get("longName")
                )
            )

        start_time = itinerary["start"]
        signature = _leg_sequence_signature(legs)
        existing_journey = journeys_by_signature.get(signature)
        if existing_journey:
            if start_time not in existing_journey.departure_options:
                existing_journey.departure_options.append(start_time)
            continue

        fare = calculate_demo_fare(
            itinerary_legs
        )

        journey = Journey(
            journey_id=f"OTP-{len(journeys_by_signature) + 1:03d}",
            origin=origin,
            destination=destination,
            departure=start_time,
            departure_options=[start_time],
            arrival=itinerary["end"],
            fare=fare,
            fare_is_estimate=True,
            walking_m=round(
                itinerary["walkDistance"]
            ),
            transfers=itinerary["numberOfTransfers"],
            legs=legs
        )

        journeys_by_signature[signature] = journey

    scheduled_journeys = list(journeys_by_signature.values())

    for journey in scheduled_journeys:
        crowding = estimate_crowding(
            origin=origin,
            destination=destination,
            departure_time=journey.departure,
            legs=journey.legs,
        )
        journey.crowding_risk = crowding["crowding_risk"]
        journey.crowding_confidence = crowding["confidence"]
        journey.crowding_summary = crowding["summary"]
        journey.crowding_is_observed = crowding["is_observed"]
        for leg in journey.legs:
            leg.crowding_risk = crowding["crowding_risk"]
            leg.crowding_confidence = crowding["confidence"]

    return scheduled_journeys