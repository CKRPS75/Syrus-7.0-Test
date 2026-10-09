def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_endpoint(client):
    response = client.get("/health/db")
    # Should succeed or return 503 depending on db reachability
    assert response.status_code in [200, 503]
