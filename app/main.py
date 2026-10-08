from fastapi import FastAPI

from app.api.journey import router as journey_router
from app.api.replan import router as replan_router
from app.api.confirm import router as confirm_router
from app.api.reports import router as reports_router


app = FastAPI(
    title="Smart Mobility Backend",
    description="Disruption-aware journey planning system",
    version="1.0.0"
)

app.include_router(journey_router)
app.include_router(replan_router)
app.include_router(confirm_router)
app.include_router(reports_router)

@app.get("/")
def home():
    return {
        "message": "Smart Mobility Backend is running!"
    }