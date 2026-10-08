import sys
import os

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.evidence.router import router as evidence_router

app = FastAPI(
    title="TrustRoute API — Evidence & Trust Engine (Person 2)",
    description=(
        "Evidence-Aware Dynamic Multimodal Journey Planner.\n"
        "Person 2 module processes crowd reports, independent news, and official alerts, "
        "performs entity and temporal grounding, detects copy-rings and contradictions, "
        "enforces the crowd-only cap (+2.6), and delivers Bayesian trust-weighted Disruption Events to Person 3."
    ),
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Evidence Router
app.include_router(evidence_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "TrustRoute Evidence & Trust Engine",
        "status": "online",
        "city": "Mumbai",
        "docs_url": "/docs",
        "endpoints": {
            "process_evidence": "POST /evidence/process",
            "list_events": "GET /evidence/events",
            "get_event": "GET /evidence/events/{event_id}",
            "config_hash": "GET /evidence/config/hash"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
