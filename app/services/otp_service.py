import requests

from app.models.journey import Journey, JourneyLeg

OTP_URL = "http://localhost:8080/otp/routers/default/index/graphql"


def calculate_demo_fare(legs):
    """
    Synthetic demo fare for the project.

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


def plan_journey(
    origin: str,
    destination: str,
    departure: str
) -> list[Journey]:

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
        transportModes: [
          { mode: WALK }
          { mode: TRANSIT }
        ]
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

    variables = {
        "fromLat": 19.0178,
        "fromLon": 72.8478,
        "toLat": 19.0760,
        "toLon": 72.8777,
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

    journeys = []

    for index, itinerary in enumerate(itineraries):

        legs = []

        for leg in itinerary["legs"]:

            route = leg.get("route")

            route_name = None

            if route:
                route_name = route.get("shortName")

            legs.append(
                JourneyLeg(
                    mode=leg["mode"],
                    from_place=leg["from"]["name"],
                    to_place=leg["to"]["name"],
                    distance_m=round(leg["distance"]),
                    duration_min=round(
                        leg["duration"] / 60
                    ),
                    route_name=route_name
                )
            )

        fare = calculate_demo_fare(
            itinerary["legs"]
        )

        journey = Journey(
            journey_id=f"OTP-{index + 1:03d}",
            origin=origin,
            destination=destination,
            departure=itinerary["start"],
            arrival=itinerary["end"],
            fare=fare,
            walking_m=round(
                itinerary["walkDistance"]
            ),
            transfers=itinerary["numberOfTransfers"],
            legs=legs
        )

        journeys.append(journey)

    return journeys