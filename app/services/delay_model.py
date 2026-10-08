def calculate_delay(
    severity: str,
    missed_connection: bool = False
) -> int:

    severity = severity.upper()

    # Demo assumptions for the project
    delay_ranges = {
        "LOW": 5,
        "MEDIUM": 15,
        "HIGH": 40
    }

    disruption_delay = delay_ranges.get(
        severity,
        15
    )

    missed_connection_delay = 0

    if missed_connection:
        missed_connection_delay = 10

    total_delay = (
        disruption_delay
        + missed_connection_delay
    )

    return total_delay


def calculate_predicted_arrival(
    scheduled_arrival,
    severity: str,
    missed_connection: bool = False
):
    delay_minutes = calculate_delay(
        severity,
        missed_connection
    )

    from datetime import datetime, timedelta

    arrival = datetime.fromisoformat(
        scheduled_arrival
    )

    predicted_arrival = (
        arrival
        + timedelta(minutes=delay_minutes)
    )

    return {
        "scheduled_arrival": scheduled_arrival,
        "delay_minutes": delay_minutes,
        "predicted_arrival": predicted_arrival.isoformat()
    }