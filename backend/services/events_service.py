import uuid
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from models.schemas import EventItem
from services.json_service import JSONDataService
from services.event_search_service import EventSearchService
from utils.logger import logger


class EventsService:
    """
    Central Campus Events & Registration Management Service.
    Integrates institutional data, dynamic Google/Unstop event discovery,
    user registrations, capacity tracking, and Microsoft Calendar records.
    """

    def __init__(self, json_service: Optional[JSONDataService] = None):
        self.json_service = json_service
        self.search_service = EventSearchService()
        
        # Memory storage
        self._events: Dict[str, EventItem] = {}
        self._registrations: Dict[str, Dict[str, Any]] = {}  # reg_id -> reg_data
        self._calendar_entries: Dict[str, Dict[str, Any]] = {}  # entry_id -> entry_data

        # Preload initial events
        self._initialize_events()

    @staticmethod
    def _parse_event_date(date_str: str) -> Optional[datetime.date]:
        """Parse an event date in ISO (YYYY-MM-DD) or Indian DD-MM-YYYY format."""
        s = (date_str or "").strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _normalize_event_date(raw_date: str, raw_status: str) -> str:
        """
        Normalize an event date to ISO YYYY-MM-DD.

        The academic calendar repeats every year, so a 'Upcoming' event whose date
        has already passed is rolled forward by one year instead of being left stale.
        Missing/unparseable dates fall back to one week from today.
        """
        today = datetime.date.today()
        d = EventsService._parse_event_date(raw_date)
        if d is None:
            return (today + datetime.timedelta(days=7)).isoformat()
        if raw_status.strip().lower() == "upcoming" and d < today:
            d = d.replace(year=d.year + 1)
        return d.isoformat()

    def _initialize_events(self):
        """Loads existing Calendar_agent.json events and converts to EventItem format."""
        if self.json_service:
            cal_data = self.json_service.get_dataset("Calendar_agent")
            if isinstance(cal_data, list):
                for idx, raw in enumerate(cal_data):
                    if not isinstance(raw, dict):
                        continue
                    evt_id = str(raw.get("Event_ID", f"EVT_{idx+1}")).strip()
                    title = str(raw.get("Event_Name", "Campus Event")).strip()
                    cat = str(raw.get("Category", "Academic Calendar")).strip()
                    dept = str(raw.get("Department", "Administration")).strip()
                    s_date = str(raw.get("Start_Date", "")).strip()
                    e_date = str(raw.get("End_Date", "")).strip()
                    venue = str(raw.get("Venue", "Campus Auditorium")).strip()
                    aud = str(raw.get("Audience", "All Students")).strip()
                    org = str(raw.get("Organizer", "VCE")).strip()
                    desc = str(raw.get("Description", title)).strip()
                    raw_status = str(raw.get("Status", "Upcoming")).strip() or "Upcoming"

                    today = datetime.date.today()
                    date_str = self._normalize_event_date(s_date, raw_status)
                    # An event whose date has passed is no longer upcoming, regardless
                    # of what the static dataset says.
                    status = "Upcoming" if date_str >= today.isoformat() else "Completed"

                    # Derive a registration deadline from the event date when the
                    # dataset provides none, and never let it fall in the past.
                    parsed_date = self._parse_event_date(date_str)
                    deadline = (parsed_date - datetime.timedelta(days=1)).isoformat() if parsed_date else date_str
                    if deadline < today.isoformat():
                        deadline = today.isoformat()

                    item = EventItem(
                        id=evt_id,
                        title=title,
                        description=desc,
                        category=cat,
                        organizer=org,
                        department=dept,
                        date=date_str,
                        start_time="09:30 AM",
                        end_time="04:30 PM",
                        location=venue,
                        capacity=300 if "Hackathon" in cat or "Fest" in cat else None,
                        registration_required=True if status == "Upcoming" and "Holiday" not in cat else False,
                        registration_open=True if status == "Upcoming" else False,
                        registration_deadline=deadline,
                        registration_url=f"https://vce.ac.in/events/{evt_id.lower()}",
                        eligibility=aud,
                        status=status,
                        online=False,
                        tags=[cat.lower(), dept.lower(), "vce"],
                        source="institutional"
                    )
                    self._events[evt_id] = item

        # Merge dynamic Unstop & Google events
        external_events = self.search_service.search_external_events("workshops hackathons 2026")
        for ext in external_events:
            self._events[ext.id] = ext

        logger.info(f"EventsService initialized with {len(self._events)} total campus & external events.")

    def get_events(
        self,
        category: Optional[str] = None,
        department: Optional[str] = None,
        timeframe: Optional[str] = None,
        eligibility: Optional[str] = None,
        query: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[EventItem]:
        """
        Filter and retrieve campus & external events based on query parameters.
        """
        # Trigger real-time search if query specifies external search terms
        if query and ("unstop" in query.lower() or "google" in query.lower() or "hackathon" in query.lower()):
            fresh = self.search_service.search_external_events(query)
            for item in fresh:
                self._events[item.id] = item

        results = list(self._events.values())

        # Category Filter
        if category and category.lower() != "all":
            results = [e for e in results if category.lower() in e.category.lower()]

        # Department Filter
        if department and department.lower() != "all":
            results = [e for e in results if department.lower() in (e.department or "").lower()]

        # Timeframe Filter
        if timeframe and timeframe.lower() != "all":
            tf = timeframe.lower()
            if tf in ["upcoming", "today", "this week", "this month"]:
                results = [e for e in results if e.status == "Upcoming"]

        # Text Query Filter
        if query and query.strip():
            words = [w.lower() for w in query.strip().split() if len(w) > 2]
            results = [
                e for e in results
                if any(w in f"{e.title} {e.description} {e.category} {e.department} {e.location}".lower() for w in words)
            ]

        # Attach user registration & calendar state if user_id is provided
        if user_id:
            user_regs = self.get_user_registered_event_ids(user_id)
            user_cals = self.get_user_calendar_event_ids(user_id)
            updated_results = []
            for e in results:
                e_copy = e.model_copy()
                e_copy.is_registered = e.id in user_regs
                e_copy.calendar_added = e.id in user_cals
                updated_results.append(e_copy)
            return updated_results

        return results

    def get_event_by_id(self, event_id: str, user_id: Optional[str] = None) -> Optional[EventItem]:
        """Retrieve single event details by ID."""
        event = self._events.get(event_id)
        if not event:
            return None

        event_copy = event.model_copy()
        if user_id:
            user_regs = self.get_user_registered_event_ids(user_id)
            user_cals = self.get_user_calendar_event_ids(user_id)
            event_copy.is_registered = event_id in user_regs
            event_copy.calendar_added = event_id in user_cals

        return event_copy

    def register_user_for_event(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """
        Registers user for event following strict verification rules:
        1. Verify user authenticated
        2. Verify event exists
        3. Verify registration open
        4. Verify registration deadline
        5. Verify capacity limit
        6. Prevent duplicate registrations
        """
        if not user_id:
            return {"success": False, "message": "Authentication required.", "event_id": event_id}

        event = self._events.get(event_id)
        if not event:
            return {"success": False, "message": f"Event '{event_id}' not found.", "event_id": event_id}

        # 3. Registration open
        if not event.registration_open or event.status == "Completed":
            return {"success": False, "message": "Registration is currently closed for this event.", "event_id": event_id}

        # 4. Registration deadline check
        if event.registration_deadline:
            try:
                deadline_dt = datetime.datetime.strptime(event.registration_deadline, "%Y-%m-%d")
                if datetime.datetime.now() > deadline_dt + datetime.timedelta(days=1):
                    return {"success": False, "message": "Registration deadline has passed.", "event_id": event_id}
            except Exception:
                pass

        # 5. Capacity check
        if event.capacity and (event.registered_count or 0) >= event.capacity:
            return {"success": False, "message": "Event is fully booked. Capacity limit reached.", "event_id": event_id}

        # 6. Duplicate prevention check
        existing_reg = self.get_user_registration(user_id, event_id)
        if existing_reg and existing_reg.get("status") == "registered":
            return {"success": False, "message": "You are already registered for this event.", "event_id": event_id}


        # Create registration
        reg_id = f"reg_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        reg_data = {
            "id": reg_id,
            "event_id": event_id,
            "user_id": user_id,
            "status": "registered",
            "registered_at": now_iso,
            "created_at": now_iso
        }
        self._registrations[reg_id] = reg_data

        # Update event registered count
        event.registered_count = (event.registered_count or 0) + 1

        logger.info(f"User [{user_id}] successfully registered for event [{event_id}] (reg_id: {reg_id})")
        return {
            "success": True,
            "message": f"Registration successful for '{event.title}'.",
            "event_id": event_id,
            "registration_id": reg_id
        }

    def cancel_registration(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Cancels a user's event registration."""
        reg = self.get_user_registration(user_id, event_id)
        if not reg:
            return {"success": False, "message": "No active registration found for this event."}

        reg["status"] = "cancelled"
        reg_id = reg["id"]

        event = self._events.get(event_id)
        if event and (event.registered_count or 0) > 0:
            event.registered_count -= 1

        logger.info(f"User [{user_id}] cancelled registration [{reg_id}] for event [{event_id}]")
        return {"success": True, "message": "Registration cancelled successfully.", "event_id": event_id}

    def get_user_registration(self, user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user's active registration record for an event."""
        for r in self._registrations.values():
            if r.get("user_id") == user_id and r.get("event_id") == event_id and r.get("status") == "registered":
                return r
        return None

    def get_user_registered_event_ids(self, user_id: str) -> List[str]:
        """List event IDs registered by user."""
        return [
            r["event_id"] for r in self._registrations.values()
            if r.get("user_id") == user_id and r.get("status") == "registered"
        ]

    def record_calendar_entry(self, user_id: str, event_id: str, microsoft_event_id: str) -> Dict[str, Any]:
        """Record Microsoft Calendar event creation against user's registration."""
        entry_id = f"cal_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        entry_data = {
            "id": entry_id,
            "user_id": user_id,
            "event_id": event_id,
            "microsoft_event_id": microsoft_event_id,
            "created_at": now_iso
        }
        self._calendar_entries[entry_id] = entry_data
        return entry_data

    def get_calendar_entry(self, user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Check if user has already added event to Microsoft Calendar."""
        for c in self._calendar_entries.values():
            if c.get("user_id") == user_id and c.get("event_id") == event_id:
                return c
        return None

    def delete_calendar_entry(self, user_id: str, event_id: str) -> Optional[str]:
        """Remove calendar entry record and return Microsoft event ID."""
        for entry_id, c in list(self._calendar_entries.items()):
            if c.get("user_id") == user_id and c.get("event_id") == event_id:
                ms_id = c.get("microsoft_event_id")
                del self._calendar_entries[entry_id]
                return ms_id
        return None

    def get_user_calendar_event_ids(self, user_id: str) -> List[str]:
        """List event IDs added to Microsoft Calendar by user."""
        return [
            c["event_id"] for c in self._calendar_entries.values()
            if c.get("user_id") == user_id
        ]

    def get_my_events(self, user_id: str) -> Dict[str, List[EventItem]]:
        """Return user's registered, upcoming, and past events."""
        reg_ids = self.get_user_registered_event_ids(user_id)
        cal_ids = self.get_user_calendar_event_ids(user_id)

        registered_list = []
        for eid in reg_ids:
            evt = self._events.get(eid)
            if evt:
                copy_evt = evt.model_copy()
                copy_evt.is_registered = True
                copy_evt.calendar_added = eid in cal_ids
                registered_list.append(copy_evt)

        upcoming_list = [
            e.model_copy(update={"is_registered": e.id in reg_ids, "calendar_added": e.id in cal_ids})
            for e in self._events.values() if e.status == "Upcoming"
        ]

        past_list = [
            e.model_copy(update={"is_registered": e.id in reg_ids, "calendar_added": e.id in cal_ids})
            for e in self._events.values() if e.status == "Completed"
        ]

        return {
            "registered": registered_list,
            "upcoming": upcoming_list[:8],
            "past": past_list[:8]
        }
