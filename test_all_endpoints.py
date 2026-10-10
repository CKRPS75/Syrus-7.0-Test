"""
Master API Verification Test Suite (P2, P3, P4).
Tests all endpoints against FastAPI application without needing external servers.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_suite():
    print("=" * 70)
    print("      TRUSTROUTE MASTER API ENDPOINT VERIFICATION SUITE")
    print("=" * 70)

    # 1. Health Root
    r = client.get("/")
    assert r.status_code == 200, f"Root failed: {r.text}"
    print("[PASS] GET / -> 200 OK (Status: online)")

    # 2. Journey Plan (P3 / P4)
    r = client.post("/journey/plan", json={
        "origin": "Chembur",
        "destination": "Andheri",
        "departure": "2026-10-09T17:00:00",
        "deadline": "2026-10-09T19:00:00",
        "budget": 80.0,
        "max_walking": 1000,
        "accessibility_required": False
    })
    assert r.status_code == 200, f"/journey/plan failed: {r.text}"
    plan_data = r.json()
    assert plan_data["status"] == "SUCCESS"
    assert "journey" in plan_data
    print(f"[PASS] POST /journey/plan -> 200 OK (Fare: Rs.{plan_data['journey']['fare']}, Walking: {plan_data['journey']['walking_m']}m)")

    # 3. Evidence Processing (P2 / P4)
    r = client.post("/evidence/process", json={
        "source_id": "TEST_OFFICIAL_01",
        "source_type": "official",
        "text": "Western Railway official alert: Technical snag at Dadar station on slow line. Suburban trains delayed by 25 minutes.",
        "timestamp": "2026-10-08T18:00:00Z"
    })
    assert r.status_code == 200, f"/evidence/process failed: {r.text}"
    ev_data = r.json()
    assert ev_data["status"] == "CONFIRMED"
    print(f"[PASS] POST /evidence/process -> 200 OK (Status: {ev_data['status']}, Score: {ev_data['confidence_score']:.2f})")

    # 4. Replanning with Confirmed Disruption (P3 / P4)
    r = client.post("/replan", json={
        "origin": "Chembur",
        "destination": "Andheri",
        "departure": "2026-10-09T17:00:00",
        "deadline": "2026-10-09T19:00:00",
        "budget": 80.0,
        "max_walking": 1000,
        "report_text": "Official alert: Metro Line 1 overhead equipment failure at Andheri. Services suspended.",
        "source_type": "official",
        "source_id": "OFF_METRO_01",
        "disrupted_route": "Metro Line 1"
    })
    assert r.status_code == 200, f"/replan failed: {r.text}"
    replan_data = r.json()
    assert replan_data["decision"] == "PROPOSE"
    assert "comparison" in replan_data
    print(f"[PASS] POST /replan -> 200 OK (Decision: {replan_data['decision']}, Time Saved: {replan_data['time_saved_minutes']} min)")

    # 5. User Confirmation (P3 / P4)
    r = client.post("/confirm", json={
        "proposal_id": "PROP_MUM_001",
        "accepted": True
    })
    assert r.status_code == 200, f"/confirm failed: {r.text}"
    conf_data = r.json()
    assert conf_data["status"] == "ACCEPTED"
    print(f"[PASS] POST /confirm -> 200 OK (Status: {conf_data['status']})")

    # 6. Tourist Attractions & Tour Planner (Persona T5)
    r = client.get("/tourist/attractions")
    assert r.status_code == 200, f"/tourist/attractions failed: {r.text}"
    attractions = r.json()
    print(f"[PASS] GET /tourist/attractions -> 200 OK ({len(attractions)} Mumbai attractions loaded)")

    r = client.post("/tourist/plan", json={
        "start_location_name": "Gateway of India",
        "start_time": "09:00",
        "curfew_deadline": "19:00",
        "budget_inr": 350.0,
        "max_walking_m": 3000,
        "stops": [
            {
                "id": "crawford_market",
                "name": "Crawford Market",
                "lat": 18.9472,
                "lon": 72.8344,
                "open_time": "10:00",
                "close_time": "20:00",
                "dwell_minutes": 45,
                "priority": "HIGH",
                "fare_inr": 0.0
            },
            {
                "id": "siddhivinayak_temple",
                "name": "Siddhivinayak Temple",
                "lat": 19.0169,
                "lon": 72.8304,
                "open_time": "06:00",
                "close_time": "21:00",
                "dwell_minutes": 60,
                "priority": "MEDIUM",
                "fare_inr": 0.0
            }
        ]
    })
    assert r.status_code == 200, f"/tourist/plan failed: {r.text}"
    tour_data = r.json()
    print(f"[PASS] POST /tourist/plan -> 200 OK (Visited: {tour_data['total_stops_visited']} stops, Status: {tour_data['status']})")

    print("=" * 70)
    print("  ALL 6 MASTER API ENDPOINTS VALIDATED AND WORKING FLAWLESSLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_api_suite()
