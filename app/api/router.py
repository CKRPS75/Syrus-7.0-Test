from fastapi import APIRouter
from app.api.routes import health, journey, evidence, event, impact, replan, confirm

api_router = APIRouter()

# Health endpoints mounted directly for /health & /health/db compatibility
api_router.include_router(health.router)

# Domain routes
api_router.include_router(journey.router)
api_router.include_router(evidence.router)
api_router.include_router(event.router)
api_router.include_router(impact.router)
api_router.include_router(replan.router)
api_router.include_router(confirm.router)
