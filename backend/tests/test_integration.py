import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def client():
    # Lifespan must run so the global services (auth, orchestrator, ...) exist.
    # A bare TestClient(app) without the context manager leaves them None and
    # only worked by accident when earlier test modules had initialized them.
    with TestClient(app) as c:
        yield c


def test_api_health(client):
    """1. Test GET /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "RUDRA"
    assert data["agents_loaded"] is True


def test_api_agents(client):
    """2. Test GET /api/agents endpoint."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total"] == len(data["agents"])
    assert len(data["agents"]) >= 11
    agent_names = [a["name"] for a in data["agents"]]
    assert "academic_agent" in agent_names
    assert "faculty_agent" in agent_names
    assert "timetable_agent" in agent_names


def test_academic_query(client):
    """3. Test Academic query POST /api/chat."""
    response = client.post("/api/chat", json={"message": "What subjects are there in 2nd semester?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "academic_agent" in data["agents_used"]
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


def test_faculty_query(client):
    """4. Test Faculty query POST /api/chat."""
    response = client.post("/api/chat", json={"message": "Tell me about faculty members."})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "faculty_agent" in data["agents_used"]


def test_timetable_query(client):
    """5. Test Timetable query POST /api/chat."""
    response = client.post("/api/chat", json={"message": "What is the timetable for IT-A?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "timetable_agent" in data["agents_used"]


def test_examination_query(client):
    """6. Test Examination query POST /api/chat."""
    response = client.post("/api/chat", json={"message": "When are the exams?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "examination_agent" in data["agents_used"]


def test_multi_agent_query(client):
    """7. Test Multi-agent query POST /api/chat."""
    response = client.post("/api/chat", json={"message": "Who teaches Data Structures and when is their class?"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["agents_used"]) >= 2
    assert "faculty_agent" in data["agents_used"] or "timetable_agent" in data["agents_used"]


def test_unknown_query(client):
    """8. Test Unknown query POST /api/chat."""
    response = client.post("/api/chat", json={"message": "Tell me something completely unrelated to the campus."})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["message"], str)


def test_empty_query(client):
    """9. Test Empty query POST /api/chat."""
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "cannot be empty" in data["message"].lower()


def test_agent_failure_handling(client):
    """10. Test system resilience to invalid agent payload."""
    response = client.post("/api/chat", json={"query": "    "})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
