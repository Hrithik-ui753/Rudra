import datetime
import json
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app
from services.notification_service import NotificationService
from services.events_service import EventsService
from services.json_service import JSONDataService


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_notification_creation_and_fetching(client):
    auth_headers = {"Authorization": "Bearer user_test_notif_1"}
    
    # Fetch notifications
    res = client.get("/api/notifications", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "notifications" in data
    assert "unread_count" in data


def test_user_isolation(client):
    user_a_headers = {"Authorization": "Bearer user_test_user_a"}
    user_b_headers = {"Authorization": "Bearer user_test_user_b"}

    # Fetch notifications for user A and B
    res_a = client.get("/api/notifications", headers=user_a_headers)
    res_b = client.get("/api/notifications", headers=user_b_headers)

    notifs_a = res_a.json()["notifications"]
    notifs_b = res_b.json()["notifications"]

    # Ensure no notification belonging to User A appears in User B's list
    a_ids = [n["id"] for n in notifs_a]
    b_ids = [n["id"] for n in notifs_b]
    assert len(set(a_ids).intersection(set(b_ids))) == 0


def _write_synthetic_calendar(tmp_path, today: datetime.date) -> Path:
    """Write a Calendar_agent.json with events dated relative to today."""
    def evt(eid: str, name: str, offset_days: int, category: str = "Workshop") -> dict:
        date_str = (today + datetime.timedelta(days=offset_days)).strftime("%d-%m-%Y")
        return {
            "Event_ID": eid,
            "Event_Name": name,
            "Category": category,
            "Department": "IT" if category == "Workshop" else "Administration",
            "Start_Date": date_str,
            "End_Date": date_str,
            "Venue": "R&D Lab",
            "Audience": "All Students",
            "Organizer": "VCE",
            "Description": f"Synthetic {name} for reminder regression testing",
            "Reminder": "1 Day Before",
            "Status": "Upcoming",
        }

    cal_path = tmp_path / "Calendar_agent.json"
    cal_path.write_text(
        json.dumps([
            evt("EVT_REM_A", "Reminder Workshop", offset_days=1),
            evt("EVT_REM_B", "Deadline Fest", offset_days=2, category="Fest"),
        ]),
        encoding="utf-8",
    )
    return cal_path


def test_event_reminder_and_deadline_generation(tmp_path):
    """
    Deterministic regression test for reminder generation.

    Previously this test depended on whatever real dataset events happened to fall
    inside the 24-hour reminder window, which made it flaky (no event is guaranteed
    to start within 24h). Here a synthetic dataset pins the timing exactly:
    - EVT_REM_A starts within 24h  -> an 'event_reminder' must be created once
    - EVT_REM_B deadline is within 24h -> a 'registration_deadline' must be created
    - A second sweep must NOT duplicate any reminder (anti-spam)
    """
    today = datetime.date.today()
    _write_synthetic_calendar(tmp_path, today)

    events_service = EventsService(json_service=JSONDataService(data_dir=str(tmp_path)))
    notif_service = NotificationService()
    user_id = "user_test_reminder_gen"

    # Pin EVT_REM_A's start to exactly 5 hours from now so the 24h window always holds.
    event_dt = datetime.datetime.now() + datetime.timedelta(hours=5)
    evt_a = events_service._events["EVT_REM_A"]
    evt_a.date = event_dt.strftime("%Y-%m-%d")
    evt_a.start_time = event_dt.strftime("%H:%M")

    # Sanity: both events resolved as Upcoming with ISO dates & non-past deadlines
    assert evt_a.status == "Upcoming"
    evt_b = events_service.get_event_by_id("EVT_REM_B")
    assert evt_b.status == "Upcoming"
    assert evt_b.registration_deadline >= today.isoformat()

    # Register user for the event that starts within 24h
    reg_res = events_service.register_user_for_event(user_id=user_id, event_id="EVT_REM_A")
    assert reg_res["success"] is True

    # First sweep: reminder must be generated
    generated = notif_service.generate_event_reminders(events_service)
    assert generated >= 1

    reminders = [n for n in notif_service.get_user_notifications(user_id) if n.type == "event_reminder"]
    assert len(reminders) == 1
    assert reminders[0].event_id == "EVT_REM_A"

    # Anti-spam: second sweep must not create duplicates
    notif_service.generate_event_reminders(events_service)
    reminders_again = [n for n in notif_service.get_user_notifications(user_id) if n.type == "event_reminder"]
    assert len(reminders_again) == 1

    # Deadline reminder for EVT_REM_B (deadline within 24h) reaches demo users
    deadline_notifs = [
        n for n in notif_service._notifications.values()
        if n.get("type") == "registration_deadline" and n.get("event_id") == "EVT_REM_B"
    ]
    assert len(deadline_notifs) >= 1


def test_no_reminders_for_far_future_events(tmp_path):
    """Anti-spam regression: events outside the 24h window produce no reminders."""
    today = datetime.date.today()
    _write_synthetic_calendar(tmp_path, today)

    events_service = EventsService(json_service=JSONDataService(data_dir=str(tmp_path)))
    notif_service = NotificationService()
    user_id = "user_test_far_future"

    # Move EVT_REM_A 30 days out so it is outside the 24h reminder window
    evt_a = events_service._events["EVT_REM_A"]
    evt_a.date = (today + datetime.timedelta(days=30)).isoformat()

    reg_res = events_service.register_user_for_event(user_id=user_id, event_id="EVT_REM_A")
    assert reg_res["success"] is True

    generated = notif_service.generate_event_reminders(events_service)
    user_notifs = notif_service.get_user_notifications(user_id)
    assert generated == 0
    assert not any(n.type == "event_reminder" for n in user_notifs)


def test_duplicate_prevention_and_anti_spam(client):
    headers = {"Authorization": "Bearer user_test_dup_check"}
    
    res1 = client.get("/api/notifications", headers=headers)
    count1 = res1.json()["total"]

    # Call again immediately
    res2 = client.get("/api/notifications", headers=headers)
    count2 = res2.json()["total"]

    assert count1 == count2


def test_mark_notification_read_and_read_all(client):
    headers = {"Authorization": "Bearer user_test_read_mark"}

    res = client.get("/api/notifications", headers=headers)
    notifs = res.json()["notifications"]

    if notifs:
        target_id = notifs[0]["id"]
        mark_res = client.patch(f"/api/notifications/{target_id}/read", headers=headers)
        assert mark_res.status_code == 200
        assert mark_res.json()["success"] is True

    # Mark all read
    read_all_res = client.patch("/api/notifications/read-all", headers=headers)
    assert read_all_res.status_code == 200
    assert read_all_res.json()["success"] is True

    # Verify unread count is 0
    after_res = client.get("/api/notifications", headers=headers)
    assert after_res.json()["unread_count"] == 0


def test_next_registered_event_endpoint(client):
    headers = {"Authorization": "Bearer user_test_next_event"}

    # User with no registrations initially
    no_reg_res = client.get("/api/my-events/next", headers=headers)
    assert no_reg_res.status_code == 200
    assert no_reg_res.json()["event"] is None

    # Register for an event
    events_res = client.get("/api/events?timeframe=upcoming")
    target_evt = events_res.json()["events"][0]
    client.post(f"/api/events/{target_evt['id']}/register", headers=headers)

    # Check next event
    next_res = client.get("/api/my-events/next", headers=headers)
    assert next_res.status_code == 200
    next_data = next_res.json()
    assert next_data["success"] is True
    assert next_data["event"] is not None
    assert next_data["event"]["id"] == target_evt["id"]
