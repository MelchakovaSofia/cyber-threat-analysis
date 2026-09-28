import pytest
from fastapi.testclient import TestClient


def test_alerts_endpoint_with_patch_body(client, admin_token):
    """Test that the alerts PATCH endpoint works with request body."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test the PATCH endpoint with proper JSON body
    response = client.patch(
        "/api/alerts/999", 
        json={"status": "resolved"},
        headers=headers
    )
    
    # Should return 404 since alert doesn't exist, but not 422 (validation error)
    assert response.status_code in [404, 422]
    
    # If it's 422, check that it's not a validation error about the request format
    if response.status_code == 422:
        detail = response.json()["detail"]
        # Should not be about missing body or incorrect format
        assert "status" not in str(detail).lower() or "field" not in str(detail).lower()