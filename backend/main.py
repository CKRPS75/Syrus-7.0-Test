import sys
import os

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.evidence.router import router as evidence_router
from backend.api.journey import router as journey_router
from backend.api.replan import router as replan_router
from backend.api.confirm import router as confirm_router
from backend.api.tourist import router as tourist_router
from backend.api.auth import router as auth_router
from backend.api.analytics import router as analytics_router

configured_origins = [
    origin.strip()
    for origin in os.getenv(
        "TRUSTROUTE_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="TrustRoute Master API",
    description=(
        "Evidence-Aware Dynamic Multimodal Journey Planning System for Greater Mumbai.\n"
        "Integrates Bayesian Evidence Engine (P2), Multi-Modal OTP Routing & Replanning (P3), "
        "Persona T5 Multi-Stop Tourist Optimizer, and User Confirmation."
    ),
    version="2.0.0"
)

# CORS setup for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(journey_router)
app.include_router(replan_router)
app.include_router(confirm_router)
app.include_router(evidence_router)
app.include_router(tourist_router)
app.include_router(auth_router)
app.include_router(analytics_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "TrustRoute Master System",
        "status": "online",
        "city": "Mumbai (MMR)",
        "docs_url": "/docs",
        "personas_supported": ["T1 Commuter", "T2 Budget", "T3 Walking", "T4 Accessibility", "T5 Multi-Stop Tourist"],
        "endpoints": {
            "plan_journey": "POST /journey/plan",
            "process_evidence": "POST /evidence/process",
            "replan_journey": "POST /replan",
            "confirm_route": "POST /confirm",
            "tourist_attractions": "GET /tourist/attractions",
            "plan_tour": "POST /tourist/plan",
            "replan_tour": "POST /tourist/replan",
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "current_user": "GET /auth/me",
            "logout": "POST /auth/logout",
            "password_reset": "POST /auth/reset (not available until email is configured)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
