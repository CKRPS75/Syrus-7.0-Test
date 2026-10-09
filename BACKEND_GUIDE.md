# TrustRoute Backend Guide

A brief guide to the backend's current behavior, developer tools, and project files. This document reflects the files currently present in the workspace on 2026-10-09.

## What It Does

TrustRoute is a Python/FastAPI backend for multimodal transit journey planning and transit-disruption awareness. The current MVP describes Mumbai Bus, Metro, and Walking journeys. Clients can plan a journey, submit a disruption report, inspect an event, calculate its effect on a journey, request a replan proposal, and accept or reject a proposal.

The application is a modular monolith: the API, business services, database models, and persistence code run together in one backend process.

## How Requests Flow

```text
HTTP client
  -> FastAPI route
  -> Pydantic request schema
  -> dependency creates service/provider and database session
  -> service applies application rules
  -> repository reads/writes SQLAlchemy models
  -> PostgreSQL + PostGIS
  -> Pydantic response
```

1. `POST /journey/plan` validates a request, finds or creates its traveller, calls the mock routing provider, and saves a journey and initial itinerary.
2. `POST /evidence/process` sends the report to the mock evidence processor, then stores a report, event, and linked evidence record.
3. `GET /events/{event_id}` returns an event and its evidence. `GET /journeys/{journey_id}` returns a journey and its related traveller, itineraries, impacts, and proposals.
4. `POST /impact/check` compares event details with itinerary legs, estimates delay, and records whether the route is affected, feasible, and protected.
5. `POST /replan` asks the routing provider for alternatives, saves an alternative itinerary, and creates a pending proposal.
6. `POST /confirm` records acceptance or rejection. On acceptance, it marks the proposal's itinerary as current.

These are separate requests; processing evidence does not automatically trigger impact analysis or replanning. The client or another caller coordinates those steps.

Health endpoints are `GET /health` and `GET /health/db`. The router is mounted at both the root and `/api/v1`; use `/api/v1` for new clients. FastAPI docs are at `/docs` and `/redoc`, with OpenAPI JSON at `/api/v1/openapi.json`.

## Runtime And Developer Tools

- **Python 3.11** runs the backend and scripts.
- **FastAPI** defines HTTP APIs, dependency injection, and OpenAPI docs.
- **Pydantic v2 / pydantic-settings** validate request/response data and load configuration.
- **SQLAlchemy 2.x** maps Python models to database tables and manages database sessions.
- **Psycopg 3** is the PostgreSQL driver.
- **PostgreSQL + PostGIS** store application data and geographic event geometry.
- **Alembic** applies database schema revisions.
- **Uvicorn** serves the ASGI application.
- **Docker Compose** defines the local database and backend containers. The current compose file uses `postgis/postgis:16-3.4` and contains development credentials; do not treat those values as production secrets or production configuration.
- **pytest** runs unit and API integration tests; **httpx** is used by FastAPI's test client.

Useful local commands from an activated virtual environment:

```powershell
python -m pip install -r requirements.txt
python -m alembic upgrade head
python seed.py
python -m uvicorn app.main:app --reload
python -m pytest -q
```

The current dependency wiring always selects `MockRoutingProvider` and `MockEvidenceProcessor`. No live routing engine or external data-feed scheduler is wired into server startup. Ingestion, simulation, evaluation, and validation are helper modules.

## File And Folder Reference

### Root

| Path | Purpose |
|---|---|
| `.env.example` | Example environment settings for the app and database. |
| `.gitignore` | Excludes local secrets, environments, caches, and generated files from Git. |
| `alembic.ini` | Alembic migration command and logging configuration. |
| `docker-compose.yml` | Local PostgreSQL/PostGIS and backend services, ports, health check, and persistent DB volume. |
| `Dockerfile` | Builds the Python backend image and starts Uvicorn. |
| `README.md` | Project overview, architecture, setup, and API examples. |
| `requirements.txt` | Python application and test dependencies. |
| `seed.py` | Inserts development examples for a traveller, journey, itinerary, report, disruption, evidence, impact, and replan proposal. |

The local `.env` file is intentionally not described or reproduced because it can contain credentials. `venv/`, `.git/`, `__pycache__/`, and `.pytest_cache/` are local/generated directories and are not application source.

### `app/`

| Path | Purpose |
|---|---|
| `app/__init__.py` | Marks `app` as a Python package. |
| `app/main.py` | Creates the FastAPI application, logging, CORS, lifecycle hooks, error handling, and router mounts. |
| `app/config.py` | Defines app, database, and routing configuration loaded from environment/settings. |
| `app/dependencies.py` | Supplies database sessions and constructs services and provider implementations for routes. |
| `app/api/__init__.py` | API package marker. |
| `app/api/router.py` | Aggregates and mounts route modules. |
| `app/api/routes/__init__.py` | Route package marker. |
| `app/api/routes/health.py` | Basic process and database health endpoints. |
| `app/api/routes/journey.py` | Journey planning and journey-detail endpoints. |
| `app/api/routes/evidence.py` | Disruption report processing endpoint. |
| `app/api/routes/event.py` | Event retrieval endpoint. |
| `app/api/routes/impact.py` | Journey/event impact-check endpoint. |
| `app/api/routes/replan.py` | Alternative itinerary proposal endpoint. |
| `app/api/routes/confirm.py` | Accept/reject proposal endpoint. |
| `app/schemas/__init__.py` | Schema package marker. |
| `app/schemas/traveller.py` | Traveller preferences and traveller API shapes. |
| `app/schemas/journey.py` | Journey request/response and origin/destination coordinate schemas. |
| `app/schemas/itinerary.py` | Itinerary and route data response shapes. |
| `app/schemas/report.py` | Report fields used by the API/domain. |
| `app/schemas/evidence.py` | Evidence submission and processing response schemas. |
| `app/schemas/event.py` | Event and event-detail response schemas. |
| `app/schemas/impact.py` | Impact request and response schemas. |
| `app/schemas/replan.py` | Replan request and proposal response schemas. |
| `app/schemas/confirm.py` | Proposal decision request and confirmation response schemas. |
| `app/schemas/data_source.py` | Data-source metadata schema. |
| `app/db/__init__.py` | Database package marker. |
| `app/db/database.py` | SQLAlchemy engine, session factory, declarative base, request-session dependency, and connection helper. |
| `app/db/models.py` | SQLAlchemy enums and TrustRoute records: travellers, journeys, itineraries, events, reports, evidence, route impacts, proposals, confirmations, and data sources. |
| `app/db/repositories/__init__.py` | Repository package marker. |
| `app/db/repositories/traveller_repo.py` | Finds and creates traveller rows. |
| `app/db/repositories/journey_repo.py` | Creates and loads journeys and updates the current itinerary reference. |
| `app/db/repositories/itinerary_repo.py` | Creates, loads, and switches journey itineraries. |
| `app/db/repositories/report_repo.py` | Creates and retrieves reports. |
| `app/db/repositories/evidence_repo.py` | Creates evidence and looks it up by event. |
| `app/db/repositories/event_repo.py` | Creates, loads, lists, updates, and matches events. |
| `app/db/repositories/impact_repo.py` | Loads or creates impact records. |
| `app/db/repositories/replan_repo.py` | Creates proposals and changes proposal status. |
| `app/db/repositories/confirmation_repo.py` | Stores and retrieves proposal decisions. |
| `app/services/journey_service.py` | Orchestrates traveller lookup, route request, journey and itinerary persistence, and rollback on planning errors. |
| `app/services/event_service.py` | Calls the evidence processor and persists report, event, and evidence records. |
| `app/services/impact_service.py` | Matches an event against itinerary legs, estimates delay, and evaluates feasibility/protection. |
| `app/services/replan_service.py` | Requests alternative routes, stores an alternative itinerary, calculates estimated time saved, and creates a pending proposal. |
| `app/services/confirmation_service.py` | Applies accept/reject decisions and updates the active itinerary after acceptance. |
| `app/services/routing/base.py` | Abstract interface for route planning, alternatives, and arrival estimates. |
| `app/services/routing/mock_provider.py` | Deterministic demo route and alternative-route implementation. |
| `app/services/evidence/base.py` | Abstract interface for parsing raw reports into event/evidence/report data. |
| `app/services/evidence/mock_processor.py` | Mock report parser used by current dependency wiring. |

### `alembic/`

| Path | Purpose |
|---|---|
| `alembic/env.py` | Connects Alembic to app configuration and SQLAlchemy model metadata for migrations/autogeneration. |
| `alembic/script.py.mako` | Template Alembic uses to create migration revision files. |
| `alembic/versions/001_initial_schema.py` | Initial database schema revision; creates TrustRoute tables and enables PostGIS. |

The current workspace contains only migration `001`; this guide does not assume any later revisions are present.

### `cities/mumbai/`

| Path | Purpose |
|---|---|
| `cities/mumbai/config.json` | General Mumbai-specific settings. |
| `cities/mumbai/fares.json` | Fare parameters by transit mode. |
| `cities/mumbai/delay_model.json` | Severity-to-delay values used by the MVP. |
| `cities/mumbai/accessibility.json` | Accessibility configuration data. |
| `cities/mumbai/metadata.json` | Descriptive metadata about the city profile. |

### Supporting Modules

| Path | Purpose |
|---|---|
| `ingestion/__init__.py` | Ingestion package marker. |
| `ingestion/alerts/adapter.py` | Adapts alert-like input to the report/evidence domain format. |
| `ingestion/crowd/adapter.py` | Normalizes crowd-sourced report input. |
| `ingestion/gdelt/adapter.py` | Adapter scaffold for GDELT/news-style input. |
| `ingestion/gtfs/adapter.py` | Adapter scaffold for GTFS or GTFS-realtime alert input. |
| `simulator/__init__.py` | Simulator package marker. |
| `simulator/simulator.py` | Generates sample disruption reports for manual or test scenarios. |
| `evaluation/__init__.py` | Evaluation package marker. |
| `evaluation/evaluator.py` | Summarizes proposal count, average estimated time saved, acceptance rate, and calibration metric. |
| `validation/__init__.py` | Validation package marker. |
| `validation/validator.py` | Lightweight feed/report validation scaffold, not a full external-feed validator. |

These modules are not automatically run by FastAPI startup in the current code.

### `tests/`

| Path | Purpose |
|---|---|
| `tests/__init__.py` | Test package marker. |
| `tests/conftest.py` | Shared fixtures, in-memory SQLite setup, and compatibility handling for PostgreSQL/PostGIS types. |
| `tests/integration/__init__.py` | Integration-test package marker. |
| `tests/integration/test_health.py` | Health and API documentation checks. |
| `tests/integration/test_journey.py` | Journey API behavior, including planning failure behavior. |
| `tests/integration/test_evidence.py` | Evidence processing and event retrieval behavior. |
| `tests/integration/test_impact.py` | Impact-check API and service behavior. |
| `tests/integration/test_replan.py` | Replan and confirmation workflow behavior. |
| `tests/unit/__init__.py` | Unit-test package marker. |
| `tests/unit/test_delay_model.py` | Delay calculation behavior. |
| `tests/unit/test_models.py` | SQLAlchemy model mapping and table behavior. |
| `tests/unit/test_schemas.py` | Pydantic schema validation/serialization. |
| `tests/unit/test_services.py` | Service-level behavior. |

Tests use SQLite for speed. They do not by themselves prove that migrations, PostGIS queries, Docker services, or any external transit system work in a live deployment.
