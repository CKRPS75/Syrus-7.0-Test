import uuid


def test_impact_check_flow(client):
    # Create journey
    plan_res = client.post("/journey/plan", json={
        "traveller_id": str(uuid.uuid4()),
        "origin": {"name": "A", "latitude": 19.1, "longitude": 72.8},
        "destination": {"name": "B", "latitude": 19.2, "longitude": 72.9}
    })
    journey_id = plan_res.json()["id"]

    # Process evidence to get event
    ev_res = client.post("/evidence/process", json={
        "source_type": "CROWD",
        "source_name": "Alert",
        "raw_text": "Flooding on BEST Bus 351 route."
    })
    event_id = ev_res.json()["event_id"]

    # Check impact
    impact_res = client.post("/impact/check", json={
        "journey_id": journey_id,
        "event_id": event_id
    })
    assert impact_res.status_code == 200
    imp_data = impact_res.json()
    assert imp_data["journey_id"] == journey_id
    assert imp_data["event_id"] == event_id
    assert "route_feasible" in imp_data
    assert "route_protected" in imp_data
