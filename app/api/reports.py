from fastapi import APIRouter

from app.services.report_processor import process_crowd_reports


router = APIRouter(
    prefix="/reports",
    tags=["Crowd Reports"]
)


@router.get("/process")
def process_reports():

    return process_crowd_reports(
        official_confirmed=True,
        news_confirmed=True
    )