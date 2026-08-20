import uuid
import datetime
from typing import List, Dict, Any, Optional
from models.schemas import NotificationItem, EventItem
from services.events_service import EventsService
from utils.logger import logger


class NotificationService:
    """
    Central Notification & Reminder Service for RUDRA Smart Campus.
    Generates meaningful, non-spam notifications for upcoming registered events,
    event start times, and registration deadlines with strict user isolation and duplicate prevention.
    """

    def __init__(self):
        # In-memory storage: id -> notification_dict
        self._notifications: Dict[str, Dict[str, Any]] = {}
        # Preferences per user: user_id -> dict
        self._preferences: Dict[str, Dict[str, bool]] = {}

    def get_user_preferences(self, user_id: str) -> Dict[str, bool]:
        """Returns notification preferences for user (default enabled=true)."""
        return self._preferences.get(user_id, {
            "event_reminders": True,
            "deadline_reminders": True
        })

    def update_user_preferences(self, user_id: str, patch: Dict[str, bool]) -> Dict[str, bool]:
        """Update notification preferences for user."""
        prefs = self.get_user_preferences(user_id)
        prefs.update(patch)
        self._preferences[user_id] = prefs
        return prefs

    def create_notification(
        self,
        user_id: str,
        event_id: Optional[str],
        type: str,
        title: str,
        message: str,
        scheduled_for: Optional[str] = None
    ) -> NotificationItem:
        """Create and store a new notification for a user."""
        nid = f"notif_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sched_iso = scheduled_for or now_iso

        notif_dict = {
            "id": nid,
            "user_id": user_id,
            "event_id": event_id,
            "type": type,
            "title": title,
            "message": message,
            "scheduled_for": sched_iso,
            "sent_at": now_iso,
            "read_at": None,
            "created_at": now_iso
        }
        self._notifications[nid] = notif_dict
        logger.info(f"Created notification [{type}] for user [{user_id}]: '{title}'")
        return NotificationItem(**notif_dict)

    def get_user_notifications(self, user_id: str, unread_only: bool = False, events_service: Optional[EventsService] = None) -> List[NotificationItem]:
        """Retrieve all notifications for a specific authenticated user."""
        results = []
        for n in self._notifications.values():
            if n.get("user_id") == user_id:
                if unread_only and n.get("read_at") is not None:
                    continue

                copy_n = dict(n)
                # Attach event title if event_service is present
                if events_service and copy_n.get("event_id"):
                    evt = events_service.get_event_by_id(copy_n["event_id"])
                    if evt:
                        copy_n["event_title"] = evt.title

                results.append(NotificationItem(**copy_n))

        # Sort by creation time descending (latest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results

    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark single user notification as read."""
        n = self._notifications.get(notification_id)
        if not n:
            return False
        if n.get("user_id") != user_id:
            logger.warning(f"User [{user_id}] unauthorized attempt to mark notification [{notification_id}]")
            return False

        n["read_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return True

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for user as read."""
        count = 0
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for n in self._notifications.values():
            if n.get("user_id") == user_id and n.get("read_at") is None:
                n["read_at"] = now_iso
                count += 1
        return count

    @staticmethod
    def _parse_event_start(evt: EventItem) -> Optional[datetime.datetime]:
        """Parse an event's start datetime from its (ISO or DD-MM-YYYY) date and time strings."""
        date_part = (evt.date or "").strip()
        start_time = (evt.start_time or "09:00").strip()

        d = None
        for date_fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                d = datetime.datetime.strptime(date_part, date_fmt)
                break
            except ValueError:
                continue
        if d is None:
            return None

        for time_fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I %p"):
            try:
                t = datetime.datetime.strptime(start_time, time_fmt).time()
                return d.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            except ValueError:
                continue
        return d.replace(hour=9, minute=0, second=0, microsecond=0)

    def generate_event_reminders(self, events_service: EventsService) -> int:
        """
        Scans all user event registrations and deadlines to generate timely reminders.
        Enforces strict duplicate prevention and anti-spam rules:
        - 'event_reminder'   only within 24 hours before the event starts
        - 'event_starting'   only within 1 hour before the event starts
        - 'registration_deadline' only within 24 hours before the deadline
        """
        if not events_service:
            return 0

        generated_count = 0
        now = datetime.datetime.now()

        # 1. Registered Event Reminders (24h before & 1h starting soon)
        for reg in events_service._registrations.values():
            if reg.get("status") != "registered":
                continue

            user_id = reg.get("user_id")
            event_id = reg.get("event_id")
            if not user_id or not event_id:
                continue

            evt = events_service.get_event_by_id(event_id)
            if not evt or evt.status == "Completed":
                continue

            # Check if user opted out of event reminders
            prefs = self.get_user_preferences(user_id)
            if not prefs.get("event_reminders", True):
                continue

            event_dt = self._parse_event_start(evt)
            if event_dt is None:
                event_dt = now + datetime.timedelta(days=1)

            # Skip if event already ended (allow a small grace window)
            if now > event_dt + datetime.timedelta(hours=4):
                continue

            time_diff = (event_dt - now).total_seconds()

            # Check if 24h event_reminder is due (once)
            if 0 < time_diff <= 24 * 3600:
                already_reminded = any(
                    n.get("user_id") == user_id and n.get("event_id") == event_id and n.get("type") == "event_reminder"
                    for n in self._notifications.values()
                )
                if not already_reminded:
                    self.create_notification(
                        user_id=user_id,
                        event_id=event_id,
                        type="event_reminder",
                        title=f"Upcoming Registered Event: {evt.title}",
                        message=f"You registered for {evt.title} scheduled for {evt.date} at {evt.start_time} ({evt.location}).",
                        scheduled_for=(event_dt - datetime.timedelta(days=1)).isoformat()
                    )
                    generated_count += 1

            # Check if 1h event_starting reminder is due (once)
            if 0 < time_diff <= 3600:
                already_starting = any(
                    n.get("user_id") == user_id and n.get("event_id") == event_id and n.get("type") == "event_starting"
                    for n in self._notifications.values()
                )
                if not already_starting:
                    self.create_notification(
                        user_id=user_id,
                        event_id=event_id,
                        type="event_starting",
                        title=f"Event Starting Soon: {evt.title}",
                        message=f"{evt.title} is starting shortly at {evt.location}.",
                        scheduled_for=now.isoformat()
                    )
                    generated_count += 1

        # 2. Registration Deadline Reminders (only within 24h of the deadline)
        all_events = events_service.get_events()
        for evt in all_events:
            if not evt.registration_open or not evt.registration_deadline or evt.status == "Completed":
                continue

            try:
                deadline_dt = datetime.datetime.strptime(evt.registration_deadline, "%Y-%m-%d")
            except Exception:
                continue

            # Only notify when the deadline is genuinely near (within 24h)
            deadline_diff = (deadline_dt - now).total_seconds()
            if not (0 < deadline_diff <= 24 * 3600):
                continue

            # Create deadline notification for active registered or demo users
            for user_id in ["user_student", "user_faculty", "user_guest"]:
                already_deadline_notified = any(
                    n.get("user_id") == user_id and n.get("event_id") == evt.id and n.get("type") == "registration_deadline"
                    for n in self._notifications.values()
                )
                if not already_deadline_notified:
                    self.create_notification(
                        user_id=user_id,
                        event_id=evt.id,
                        type="registration_deadline",
                        title=f"Registration Closing Soon: {evt.title}",
                        message=f"Registration deadline for {evt.title} is approaching on {evt.registration_deadline}.",
                        scheduled_for=(deadline_dt - datetime.timedelta(days=1)).isoformat()
                    )
                    generated_count += 1

        return generated_count

    def get_next_registered_event(self, user_id: str, events_service: EventsService) -> Optional[EventItem]:
        """Retrieves user's nearest upcoming registered event."""
        registered_ids = events_service.get_user_registered_event_ids(user_id)
        if not registered_ids:
            return None

        upcoming_registered = []
        for eid in registered_ids:
            evt = events_service.get_event_by_id(eid, user_id=user_id)
            if evt and evt.status == "Upcoming":
                upcoming_registered.append(evt)

        if not upcoming_registered:
            return None

        # Sort by date
        upcoming_registered.sort(key=lambda x: x.date or "9999-99-99")
        return upcoming_registered[0]
