import uuid


def test_replan_and_confirm_workflow(client):
    # 1. Plan journey
    plan_res = client.post("/journey/plan", json={
        "traveller_id": str(uuid.uuid4()),
        "origin": {"name": "A", "latitude": 19.1, "longitude": 72.8},
        "destination": {"name": "B", "latitude": 19.2, "longitude": 72.9}
    })
    journey_id = plan_res.json()["id"]

    # 2. Process event
    ev_res = client.post("/evidence/process", json={
        "source_type": "CROWD",
        "source_name": "Traffic News",
        "raw_text": "Flooding on BEST Bus 351 route."
    })
    event_id = ev_res.json()["event_id"]

    # 3. Create Replan Proposal
    replan_res = client.post("/replan", json={
        "journey_id": journey_id,
        "event_id": event_id
    })
    assert replan_res.status_code == 201
    prop_data = replan_res.json()
    proposal_id = prop_data["id"]
    assert prop_data["status"] == "PENDING"
    assert prop_data["time_saved"] >= 0

    # 4. Confirm Replan Proposal (ACCEPT)
    confirm_res = client.post("/confirm", json={
        "proposal_id": proposal_id,
        "decision": "ACCEPT"
    })
    assert confirm_res.status_code == 200
    conf_data = confirm_res.json()
    assert conf_data["decision"] == "ACCEPT"
    assert conf_data["proposal_status"] == "ACCEPTED"
    assert conf_data["current_itinerary_id"] == prop_data["new_itinerary_id"]

    # 5. Try confirming again (Conflict error: not in PENDING state)
    second_confirm = client.post("/confirm", json={
        "proposal_id": proposal_id,
        "decision": "REJECT"
    })
    assert second_confirm.status_code == 409
