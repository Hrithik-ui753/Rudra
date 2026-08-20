import datetime
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app
from services.events_service import EventsService


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_events_list_endpoint(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "events" in data
    assert isinstance(data["events"], list)
    assert len(data["events"]) > 0


def test_events_filtering(client):
    # Filter by workshop
    response = client.get("/api/events?category=Workshop")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for evt in data["events"]:
        assert "workshop" in evt["category"].lower() or "workshop" in evt["title"].lower() or "workshop" in (evt["description"] or "").lower()


def test_event_detail_endpoint(client):
    response = client.get("/api/events")
    events = response.json()["events"]
    first_id = events[0]["id"]

    detail_res = client.get(f"/api/events/{first_id}")
    assert detail_res.status_code == 200
    d_data = detail_res.json()
    assert d_data["success"] is True
    assert d_data["event"]["id"] == first_id


def test_event_registration_and_duplicate_check(client):
    auth_headers = {"Authorization": "Bearer user_test_student"}
    
    # 1. Get an upcoming event
    events_res = client.get("/api/events?timeframe=upcoming")
    events = events_res.json()["events"]
    target_event = None
    for e in events:
        if e["registration_open"] and e["status"] == "Upcoming":
            target_event = e
            break

    assert target_event is not None
    evt_id = target_event["id"]

    # 2. Register for event
    reg_res = client.post(f"/api/events/{evt_id}/register", headers=auth_headers)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert "registration_id" in reg_data

    # 3. Check registration status
    status_res = client.get(f"/api/events/{evt_id}/registration", headers=auth_headers)
    assert status_res.status_code == 200
    assert status_res.json()["is_registered"] is True

    # 4. Duplicate registration attempt should return success: False
    dup_res = client.post(f"/api/events/{evt_id}/register", headers=auth_headers)
    assert dup_res.status_code == 200
    dup_data = dup_res.json()
    assert dup_data["success"] is False
    assert "already registered" in dup_data["message"].lower()

    # 5. Cancel registration
    cancel_res = client.delete(f"/api/events/{evt_id}/register", headers=auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["success"] is True

    # 6. Verify cancelled
    status_after = client.get(f"/api/events/{evt_id}/registration", headers=auth_headers)
    assert status_after.json()["is_registered"] is False


def test_microsoft_calendar_addition(client):
    auth_headers = {"Authorization": "Bearer user_test_student"}
    evt_id = "evt_unstop_01"

    # Add to calendar
    cal_res = client.post(f"/api/events/{evt_id}/calendar", json={"access_token": "mock_token"}, headers=auth_headers)
    assert cal_res.status_code == 200
    cal_data = cal_res.json()
    assert cal_data["success"] is True
    assert "calendar_event_id" in cal_data

    # Duplicate calendar addition
    dup_cal = client.post(f"/api/events/{evt_id}/calendar", json={"access_token": "mock_token"}, headers=auth_headers)
    assert dup_cal.status_code == 200
    assert "already added" in dup_cal.json()["message"].lower()

    # Delete calendar entry
    del_cal = client.request("DELETE", f"/api/events/{evt_id}/calendar", json={"access_token": "mock_token"}, headers=auth_headers)
    assert del_cal.status_code == 200
    assert del_cal.json()["success"] is True



def test_my_events_endpoint(client):
    auth_headers = {"Authorization": "Bearer user_test_student"}
    res = client.get("/api/my-events", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "registered" in data
    assert "upcoming" in data
    assert "past" in data


def test_upcoming_events_are_iso_and_never_past():
    """
    Regression: DD-MM-YYYY dates in the dataset are normalized to ISO and no
    'Upcoming' event may carry a past date (previously stale dates like the
    hardcoded 2026-08-14 deadline left registration permanently broken).
    """
    with TestClient(app) as c:
        res = c.get("/api/events?timeframe=upcoming")
    assert res.status_code == 200
    events = res.json()["events"]
    assert len(events) > 0
    today = datetime.date.today()
    for evt in events:
        try:
            evt_date = datetime.datetime.strptime(evt["date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            pytest.fail(f"Event {evt['id']}: date {evt['date']!r} is not ISO YYYY-MM-DD")
        assert evt_date >= today, f"Upcoming event {evt['id']} has past date {evt['date']}"
        if evt.get("registration_deadline"):
            try:
                deadline = datetime.datetime.strptime(evt["registration_deadline"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pytest.fail(f"Event {evt['id']}: deadline {evt['registration_deadline']!r} is not ISO")
            assert deadline >= today, f"Event {evt['id']} has past registration deadline {evt['registration_deadline']}"


def test_event_date_normalization_unit():
    """Unit regression for EventsService._parse_event_date / _normalize_event_date."""
    today = datetime.date.today()

    # DD-MM-YYYY and ISO formats both parse
    assert EventsService._parse_event_date("31-12-2026") == datetime.date(2026, 12, 31)
    assert EventsService._parse_event_date("2026-12-31") == datetime.date(2026, 12, 31)
    assert EventsService._parse_event_date("garbage") is None

    # 'Upcoming' event with a past date rolls forward one year
    past = today - datetime.timedelta(days=5)
    assert EventsService._normalize_event_date(past.strftime("%d-%m-%Y"), "Upcoming") == \
        past.replace(year=past.year + 1).isoformat()

    # 'Completed' past event keeps its date
    assert EventsService._normalize_event_date(past.isoformat(), "Completed") == past.isoformat()

    # Today's date stays put
    assert EventsService._normalize_event_date(today.isoformat(), "Upcoming") == today.isoformat()

    # Missing/unparseable dates fall back to one week from today
    assert EventsService._normalize_event_date("", "Upcoming") == \
        (today + datetime.timedelta(days=7)).isoformat()
