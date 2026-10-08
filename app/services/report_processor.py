from app.data.crowd_reports import CROWD_REPORTS
from app.models.crowd_report import CrowdReport
from app.services.confidence_engine import (
    merge_duplicate_reports,
    remove_stale_reports,
    calculate_confidence
)


def process_crowd_reports(
    official_confirmed: bool = False,
    news_confirmed: bool = False
) -> dict:

    # Convert sample dictionaries into CrowdReport objects
    reports = [
        CrowdReport(
            **report,
            confidence=0.0
        )
        for report in CROWD_REPORTS
    ]

    # Remove old reports
    active_reports = remove_stale_reports(
        reports,
        max_age_minutes=60
    )

    # Merge duplicate reports
    merged_reports = merge_duplicate_reports(
        active_reports
    )

    # Calculate overall confidence
    confidence = calculate_confidence(
        merged_reports,
        official_confirmed=official_confirmed,
        news_confirmed=news_confirmed
    )

    # Consider disruption confirmed when confidence is high
    confirmed = confidence >= 0.70

    return {
        "total_reports": len(reports),
        "active_reports": len(active_reports),
        "merged_reports": len(merged_reports),
        "confidence": confidence,
        "confirmed": confirmed,
        "official_confirmed": official_confirmed,
        "news_confirmed": news_confirmed,
        "reports": merged_reports
    }