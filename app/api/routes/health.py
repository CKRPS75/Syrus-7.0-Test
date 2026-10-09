from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.database import check_db_connection
from app.dependencies import get_db

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic service health check")
def health_check():
    return {"status": "ok"}


@router.get("/health/db", summary="Database connection health check")
def db_health_check(db: Session = Depends(get_db)):
    is_connected = check_db_connection(db.get_bind())
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "database": "disconnected"}
        )
    return {"status": "ok", "database": "connected"}
