import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app


def test_health_endpoint():
    """Verify GET /api/health returns 200 and status ok."""
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"


def test_agents_endpoint():
    """Verify GET /api/agents returns list of registered agents."""
    with TestClient(app) as client:
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "agents" in data
        assert len(data["agents"]) >= 11


def test_auth_and_profile_endpoints():
    """Verify login, profile GET/PUT, and history endpoints."""
    with TestClient(app) as client:
        # Login
        login_res = client.post("/api/auth/login", json={"email": "student@campus.edu", "role": "student"})
        assert login_res.status_code == 200
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Profile GET
        prof_res = client.get("/api/profile", headers=headers)
        assert prof_res.status_code == 200
        assert prof_res.json()["role"] == "student"

        # Profile PUT
        put_res = client.put("/api/profile", json={"branch": "CIVIL", "year": "2nd Year"}, headers=headers)
        assert put_res.status_code == 200
        assert put_res.json()["year"] == "2nd Year"


def test_chat_endpoint_with_auth():
    """Verify POST /api/chat handles natural language queries and stores history."""
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer user_student"}
        response = client.post(
            "/api/chat",
            json={"query": "What subjects are in 2nd semester?", "session_id": "test_sess_1"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert len(data.get("agents_used", [])) > 0
        assert "response" in data
        assert "suggested_followups" in data

        # Check history endpoint
        hist_res = client.get("/api/history", headers=headers)
        assert hist_res.status_code == 200
        msgs = hist_res.json()["messages"]
        assert len(msgs) >= 2
