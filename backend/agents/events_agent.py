from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult, EventItem
from services.json_service import JSONDataService
from services.events_service import EventsService
from utils.logger import logger


class EventsAgent(BaseAgent):
    """
    Events & Activities Agent responsible for campus events, workshops, hackathons,
    seminars, technical fests, cultural events, club competitions, and guest lectures.
    """

    def __init__(self, json_service: JSONDataService, events_service: Optional[EventsService] = None):
        super().__init__(
            name="events_agent",
            description="Handles campus events, workshops, hackathons, technical fests, cultural events, guest lectures, registrations, and Microsoft Calendar integration.",
            supported_queries=[
                "What events are happening?",
                "What workshops are happening this week?",
                "Are there any hackathons?",
                "Show me technical events",
                "What events can IT students attend?",
                "When is the registration deadline?",
                "Which events are happening tomorrow?",
                "Show upcoming events",
                "Are registrations open?",
                "Which events are free?",
                "Which events are organized by the CSE department?"
            ],
            json_service=json_service
        )
        self.events_service = events_service or EventsService(json_service=json_service)

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        query_lower = query.lower()
        user_id = context.get("user_id") if context else None

        # Extract Category filter
        category = None
        if "workshop" in query_lower:
            category = "Workshop"
        elif "hackathon" in query_lower:
            category = "Hackathon"
        elif "seminar" in query_lower:
            category = "Seminar"
        elif "contest" in query_lower or "coding" in query_lower:
            category = "Coding Contest"
        elif "guest" in query_lower or "lecture" in query_lower or "talk" in query_lower:
            category = "Guest"
        elif "cultural" in query_lower or "fest" in query_lower:
            category = "Cultural"
        elif "fdp" in query_lower:
            category = "FDP"

        # Extract Department filter
        department = None
        if "cse" in query_lower:
            department = "CSE"
        elif "it" in query_lower:
            department = "IT"
        elif "eee" in query_lower:
            department = "EEE"
        elif "civil" in query_lower:
            department = "CIVIL"

        # Timeframe
        timeframe = None
        if "today" in query_lower or "tomorrow" in query_lower:
            timeframe = "today"
        elif "week" in query_lower:
            timeframe = "this week"
        elif "month" in query_lower:
            timeframe = "this month"

        # Check for registered events / next event query
        if any(k in query_lower for k in ["registered for", "my events", "my registered", "next event", "coming up next", "reminders", "reminder"]):
            reg_ids = self.events_service.get_user_registered_event_ids(user_id or "user_student")
            if "next" in query_lower or "coming up" in query_lower:
                next_evt = None
                for eid in reg_ids:
                    e = self.events_service.get_event_by_id(eid, user_id=user_id)
                    if e and e.status == "Upcoming":
                        next_evt = e
                        break
                
                if next_evt:
                    answer = (
                        f"Your Next Registered Event is **{next_evt.title}**!\n"
                        f"• Date & Time: {next_evt.date} ({next_evt.start_time})\n"
                        f"• Location: {next_evt.location}\n"
                        f"• Category: {next_evt.category} | Organizer: {next_evt.organizer}"
                    )
                    ev = self.create_evidence(
                        source_type="structured_data",
                        source_name="User Event Registrations",
                        source_file="Calendar_agent.json",
                        retrieval_method="exact_lookup",
                        records_matched=1,
                        filters={"user_id": user_id or "user_student", "status": "Upcoming"},
                        relevance=0.98,
                        verified=True
                    )
                    return AgentResult(
                        agent_name=self.name,
                        success=True,
                        confidence=0.98,
                        answer=answer,
                        data={"event": next_evt.model_dump(), "events": [next_evt.model_dump()], "card_type": "event"},
                        evidence=[ev]
                    )

            if reg_ids:
                reg_events = [self.events_service.get_event_by_id(eid, user_id=user_id) for eid in reg_ids]
                reg_events = [e for e in reg_events if e]
                lines = [f"You are registered for {len(reg_events)} Campus Event(s):\n"]
                for idx, e in enumerate(reg_events):
                    lines.append(f"{idx+1}. **{e.title}** ({e.category}) - {e.date} at {e.location}")
                ev = self.create_evidence(
                    source_type="structured_data",
                    source_name="User Event Registrations",
                    source_file="Calendar_agent.json",
                    retrieval_method="exact_lookup",
                    records_matched=len(reg_events),
                    filters={"user_id": user_id or "user_student"},
                    relevance=0.95,
                    verified=True
                )
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    confidence=0.95,
                    answer="\n".join(lines),
                    data={"events": [e.model_dump() for e in reg_events], "card_type": "event"},
                    evidence=[ev]
                )
            else:
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    confidence=0.90,
                    answer="You are not currently registered for any upcoming events. You can explore workshops and hackathons in the Campus Events section!",
                    data={"events": [], "card_type": "event"},
                    evidence=[]
                )

        # Retrieve events
        events = self.events_service.get_events(
            category=category,
            department=department,
            timeframe=timeframe,
            query=query,
            user_id=user_id
        )

        if not events:
            # Fallback to all upcoming events
            events = self.events_service.get_events(timeframe="upcoming", user_id=user_id)

        # Format events list summary
        event_dicts = [e.model_dump() for e in events[:6]]

        lines = [f"Found {len(events)} Events & Activities:\n"]
        for idx, e in enumerate(events[:5]):
            reg_status = "Registration Open" if e.registration_open else "Registration Closed"
            date_info = f"Date: {e.date} ({e.start_time})" if e.date else "Upcoming"
            source_tag = " (External Opportunity)" if getattr(e, "source", "") != "institutional" and e.organizer != "VCE" else ""
            lines.append(
                f"{idx+1}. **{e.title}** ({e.category}){source_tag}\n"
                f"   • {date_info} | Venue: {e.location}\n"
                f"   • Department/Organizer: {e.department or e.organizer}\n"
                f"   • Status: {reg_status} | Deadline: {e.registration_deadline or 'N/A'}\n"
            )

        answer_text = "\n".join(lines)

        # Generate Evidence distinguishing institutional vs external events
        evidence_list = []
        inst_events = [e for e in events if getattr(e, "source", "institutional") == "institutional"]
        ext_events = [e for e in events if getattr(e, "source", "institutional") != "institutional"]

        if inst_events:
            filters_dict = {}
            if category: filters_dict["category"] = category
            if department: filters_dict["department"] = department
            if timeframe: filters_dict["timeframe"] = timeframe

            evidence_list.append(self.create_evidence(
                source_type="structured_data",
                source_name="College Academic Calendar",
                source_file="Calendar_agent.json",
                retrieval_method="filtered_json",
                records_matched=len(inst_events),
                filters=filters_dict or {"query": query},
                relevance=0.95,
                verified=True
            ))

        if ext_events:
            ext_provider = ext_events[0].organizer if ext_events[0].organizer and ext_events[0].organizer != "VCE" else "External Opportunity"
            evidence_list.append(self.create_evidence(
                source_type="external_web",
                source_name=ext_provider,
                source_file=None,
                retrieval_method="external_search",
                records_matched=len(ext_events),
                filters={"category": category, "query": query} if category else {"query": query},
                relevance=0.90,
                verified=True,
                metadata={"provider": ext_provider, "is_external": True}
            ))

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.95,
            answer=answer_text,
            data={
                "dataset": "events_and_activities",
                "total_events": len(events),
                "events": event_dicts,
                "card_type": "event"
            },
            evidence=evidence_list
        )

