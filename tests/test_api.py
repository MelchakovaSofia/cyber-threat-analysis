LOG = {
    "ip_address": "10.0.0.5",
    "timestamp": "2026-09-01T10:15:00",
    "protocol": "TCP",
    "port": 443,
    "bytes_sent": 1200,
    "bytes_received": 800,
    "status": "ok",
}


def test_create_and_list_logs(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    created = client.post("/api/logs", json=LOG, headers=headers)
    assert created.status_code == 201

    listed = client.get("/api/logs", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


def test_stats_endpoint(client, admin_token):
    response = client.get(
        "/api/analysis/stats", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "analyzed_events" in response.json()


def test_threat_detail_not_found(client, admin_token):
    response = client.get(
        "/api/analysis/results/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
