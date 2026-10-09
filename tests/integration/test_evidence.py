def test_evidence_process_flow(client):
    payload = {
        "source_type": "CROWD",
        "source_name": "Twitter Rains Alert",
        "raw_text": "Waterlogging reported on Metro Line 1 corridor near Dadar.",
        "latitude": 19.0178,
        "longitude": 72.8478
    }

    # 1. Process evidence
    res = client.post("/evidence/process", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "event_id" in data
    assert "report_id" in data
    event_id = data["event_id"]

    # 2. Retrieve event
    get_res = client.get(f"/events/{event_id}")
    assert get_res.status_code == 200
    event_data = get_res.json()
    assert event_data["id"] == event_id
    assert event_data["event_type"] == "FLOODING"
