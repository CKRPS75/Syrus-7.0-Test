# TrustRoute Project Brief

## 1) Tech Stack

The project is built as a modular backend foundation for an evidence-aware, multimodal journey planner, with a frontend layer for user interaction and map-based demonstration.

- Backend: Python 3.11+, FastAPI
- API validation: Pydantic v2
- Data layer: SQLAlchemy 2.x, Alembic, PostgreSQL 16 + PostGIS
- Runtime/infra: Docker and Docker Compose
- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS, MapLibre GL, Framer Motion
- Testing: pytest and Vitest
- Core domain logic: route planning, disruption simulation, evidence processing, replan logic, and delay modeling

This combination supports a scalable API-first architecture while keeping the system easy to demo, test, and evolve with real routing and evidence feeds.

## 2) Unique Selling Points

TrustRoute is positioned around a clear user problem:

- Most travel apps optimize for the fastest or shortest route.
- They do not adequately account for whether a route is still trustworthy under real-world disruption conditions.
- TrustRoute goes beyond route optimization to answer: "Can this journey still be trusted under current disruptions, evidence, and user constraints?"

Key differentiators:

- Evidence-aware planning: routes are evaluated with disruption signals, crowd reports, and operational context rather than just static maps.
- Multimodal focus: supports Bus, Metro, and Walking in the Mumbai MVP.
- Dynamic replan logic: if risks change, the system proposes alternatives and asks for confirmation.
- Route protection logic: checks whether the route remains feasible and acceptable based on time, risk, or accessibility constraints.
- Unfamiliar-city use case: designed for travellers navigating a city they do not know well, where trust and safety matter more than pure shortest path optimization.

## 3) Proposed Solution

TrustRoute proposes a journey-planning system that combines three layers:

1. Routing layer
   - Builds the initial multimodal route between origin and destination.
   - Accounts for transport mode combinations and walking restrictions.

2. Evidence and disruption layer
   - Takes in crowd reports, official alerts, and operational disruption signals.
   - Normalizes them into impact events and evidence records.

3. Decision and replan layer
   - Evaluates delay, route feasibility, protection status, and whether the traveller should continue, reroute, or accept a fallback option.
   - Generates alternative plans and confirmation flows.

This produces a traveler experience that is not just route-aware, but risk-aware and confidence-aware.

## 4) Unique Selling Point (USP)

"Google Maps finds a route. TrustRoute determines whether that route can still be trusted."

This is the core value proposition. TrustRoute does not merely show directions; it interprets whether the route remains safe, workable, and acceptable under real-world uncertainty. That makes it particularly valuable in unfamiliar cities, disrupted transit networks, and time-sensitive travel decisions.

## 5) Implementation Plan

### Phase 1: Foundation and API contracts
- Set up FastAPI backend, PostgreSQL/PostGIS, and Alembic migrations.
- Define core entities for traveller, journey, itinerary, event, evidence, and disruption.
- Implement health checks, journey planning API, and basic persistence.

### Phase 2: Route and protection logic
- Build route planning abstraction and mock providers for Mumbai network logic.
- Add delay calculations, feasibility checks, and protection evaluation.
- Validate route outcomes for risk, walking limits, and timing constraints.

### Phase 3: Evidence and disruption processing
- Ingest and normalize disruption reports from crowd and official sources.
- Model confidence and impact scoring around events and evidence.
- Connect disruption data to journey impact and replan decisions.

### Phase 4: Replanning and user confirmation
- Generate alternative route proposals when existing plans become unreliable.
- Add confirmation flows for accept/reject decisions.
- Expose structured APIs for downstream frontend or mobile integrations.

### Phase 5: Frontend demonstration and integration
- Build a map-driven UI using Next.js and MapLibre.
- Show journey, disruption, delay, and replan states clearly for demo users.
- Connect the UI to backend API contracts for a real proof-of-concept experience.

### Phase 6: Production-readiness roadmap
- Replace mock providers with live routing and evidence feeds.
- Add stronger validation, observability, and analytics.
- Expand beyond Mumbai to more cities and additional transport modes.

## Summary

TrustRoute is a practical, product-driven solution for trustworthy multimodal travel planning in disrupted urban environments. Its core advantage is that it converts route guidance into route confidence and decision support, giving users a stronger answer than "what is the shortest path?" It answers whether the path remains dependable, realistic, and safe in the moment.
