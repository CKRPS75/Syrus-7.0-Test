# TrustRoute Backend Foundation

> **"Google Maps finds a route. TrustRoute determines whether that route can still be trusted."**

TrustRoute is an **Evidence-Aware Dynamic Multimodal Journey Planner** designed for unfamiliar-city travel. The MVP focuses on **Mumbai** using **Bus, Metro, and Walking** transit modes.

This repository contains the modular monolith backend foundation for TrustRoute built with Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2, PostgreSQL, and PostGIS.

---

## Architecture

```text
Client (Web / Mobile)
        │
     FastAPI (app/main.py)
        │
   API Routes (app/api/routes/)
        │
 Pydantic Schemas (app/schemas/)
        │
  Service Layer (app/services/)
   ├── Routing Interface (MockRoutingProvider)
   ├── Evidence Interface (MockEvidenceProcessor)
   └── Delay Model & Feasibility Evaluator
        │
 Repositories (app/db/repositories/)
        │
 SQLAlchemy 2.x (app/db/models.py)
        │
 PostgreSQL 16 + PostGIS
```

---

## Directory Structure

```text
c:\Users\j\Desktop\Syrus-7.0-Test
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Environment configuration settings
│   ├── dependencies.py          # FastAPI dependency injection
│   ├── api/
│   │   ├── router.py            # Combined API router
│   │   └── routes/              # Endpoint routes (health, journey, evidence, impact, replan, confirm)
│   ├── schemas/                 # Pydantic v2 validation schemas
│   ├── db/
│   │   ├── database.py          # SQLAlchemy 2.x engine & session setup
│   │   ├── models.py            # Typed SQLAlchemy ORM models with PostGIS
│   │   └── repositories/        # Clean CRUD repository layer
│   └── services/                # Business logic services & mock providers
│       ├── routing/             # Abstract RoutingProvider & MockRoutingProvider
│       └── evidence/            # Abstract EvidenceProcessor & MockEvidenceProcessor
├── alembic/                     # Database migrations
├── cities/mumbai/               # Mumbai city configuration (BUS, METRO, WALK)
├── ingestion/                   # Scaffolds for GTFS, GDELT, Crowd, Alerts
├── validation/                  # Scaffolds for feed and report validation
├── simulator/                   # Scaffolds for disruption simulation
├── evaluation/                  # Scaffolds for trust & replan performance evaluation
├── tests/                       # Unit & Integration pytest suite
├── seed.py                      # Development mock data seeding script
├── docker-compose.yml           # Docker setup for Postgres + PostGIS
├── Dockerfile                   # Python 3.11 backend container spec
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment configuration template
```

---

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for PostgreSQL + PostGIS)
- Git

---

## Quickstart Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Default settings:

```ini
DATABASE_URL=postgresql+psycopg://trustroute:password@localhost:5432/trustroute
APP_ENV=development
DEBUG=true
```

### 3. Start PostgreSQL / PostGIS with Docker

```bash
docker compose up -d
```

### 4. Database Migrations

Run Alembic to create database tables and enable PostGIS:

```bash
alembic upgrade head
```

### 5. Seed Development Mock Data

Populate initial demo data (travellers, journeys, reports, disruptions):

```bash
python seed.py
```

### 6. Run FastAPI Backend

```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`.

---

## API Documentation & Endpoints

Interactive Swagger UI documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Implemented Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check (`{"status": "ok"}`) |
| `GET` | `/health/db` | Database connection status |
| `POST` | `/journey/plan` | Plan initial multimodal journey (Bus, Metro, Walk) |
| `GET` | `/journeys/{journey_id}` | Retrieve full journey details, impacts & replan proposals |
| `POST` | `/evidence/process` | Process raw crowd/official report into event & evidence record |
| `GET` | `/events/{event_id}` | Retrieve disruption event information and evidence |
| `POST` | `/impact/check` | Calculate disruption delay & evaluate feasibility vs protection |
| `POST` | `/replan` | Generate alternative bypass route replan proposal |
| `POST` | `/confirm` | User confirmation (`ACCEPT` or `REJECT`) for a replan proposal |

---

## Delay Model & Route Protection Logic

### Delay Model
Synthetic delay calculation for hackathon demonstration:
$$T_{\text{arrival}} = \text{scheduled\_arrival} + \text{disruption\_delay} + \text{missed\_connection\_delay}$$

- **LOW**: 5–10 minutes
- **MEDIUM**: 10–25 minutes
- **HIGH**: 25–60 minutes

### Route Feasibility vs Route Protection
- **`route_feasible`**: Whether the traveller can physically reach the destination (e.g. alternative paths / walking available).
- **`route_protected`**: Whether the traveller's constraints (deadline, risk tolerance, walking limits) remain satisfied under the estimated disruption delay.

---

## Running Tests

Run unit and integration test suite using `pytest`:

```bash
pytest
```

To run with verbose output:

```bash
pytest -v
```

---

## Future Integrations

- **OpenTripPlanner (OTP)**: Replace `MockRoutingProvider` with live OTP GraphQL/REST client.
- **Evidence / Trust Engine**: Replace `MockEvidenceProcessor` with LLM extraction, copy-ring detection, and GDELT ingestion.
- **Frontend Integration**: Connect Next.js/React frontend to these stable API contracts.
