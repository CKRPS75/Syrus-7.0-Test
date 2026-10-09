import uuid


def test_plan_and_get_journey_flow(client):
    traveller_id = str(uuid.uuid4())

    plan_payload = {
        "traveller_id": traveller_id,
        "origin": {
            "name": "Andheri Metro Station",
            "latitude": 19.1197,
            "longitude": 72.8464
        },
        "destination": {
            "name": "Ghatkopar Station",
            "latitude": 19.0860,
            "longitude": 72.9081
        }
    }

    # 1. Plan journey
    response = client.post("/journey/plan", json=plan_payload)
    assert response.status_code == 201
    data = response.json()
    journey_id = data["id"]
    assert data["status"] == "ACTIVE"
    assert data["current_itinerary_id"] is not None

    # 2. Get journey details
    get_response = client.get(f"/journeys/{journey_id}")
    assert get_response.status_code == 200
    detail_data = get_response.json()
    assert detail_data["id"] == journey_id
    assert detail_data["current_itinerary"] is not None


def test_get_nonexistent_journey(client):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/journeys/{fake_id}")
    assert response.status_code == 404
