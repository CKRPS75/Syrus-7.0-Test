from datetime import datetime


def merge_duplicate_reports(reports: list) -> list:
    """
    Merge reports referring to the same disruption.
    """

    merged = {}

    for report in reports:

        key = (
            report.location.lower().strip(),
            (report.affected_line or "").lower().strip(),
            (report.affected_stop or "").lower().strip(),
            report.disruption_type.upper()
        )

        if key not in merged:
            merged[key] = report
        else:
            existing = merged[key]

            # Keep the latest report
            if report.reported_at > existing.reported_at:
                merged[key] = report

    return list(merged.values())


def remove_stale_reports(
    reports: list,
    max_age_minutes: int = 60
) -> list:
    """
    Remove reports older than the allowed time.
    """

    now = datetime.now()

    active_reports = []

    for report in reports:

        reported_time = report.reported_at.replace(
            tzinfo=None
        )

        age_minutes = (
            now - reported_time
        ).total_seconds() / 60

        if age_minutes <= max_age_minutes:
            active_reports.append(report)

    return active_reports


def calculate_confidence(
    reports: list,
    official_confirmed: bool = False,
    news_confirmed: bool = False
) -> float:
    """
    Calculate disruption confidence using
    crowd, official and news corroboration.
    """

    if not reports:
        return 0.0

    independent_sources = set(
        report.source
        for report in reports
    )

    score = 0.30

    # Multiple independent sources
    if len(independent_sources) >= 2:
        score += 0.20

    # Three or more reports
    if len(reports) >= 3:
        score += 0.10

    # Official confirmation
    if official_confirmed:
        score += 0.25

    # News confirmation
    if news_confirmed:
        score += 0.15

    return round(
        min(score, 1.0),
        2
    )