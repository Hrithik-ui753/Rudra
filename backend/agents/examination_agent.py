from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class ExaminationAgent(BaseAgent):
    """
    Examination Agent responsible for retrieving exam schedules, Mid1/Mid2 dates,
    semester end examinations (SEE), and academic calendar events.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="examination_agent",
            description="Handles examination schedules, Mid-term tests, SEE exams, and academic calendar dates.",
            supported_queries=[
                "When are the Mid exams?",
                "What is the exam schedule for 1st year?",
                "When do semester practicals start?",
                "Show academic calendar events"
            ],
            json_service=json_service
        )
        self.calendar_key = "Calendar_agent"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        if not self.is_dataset_available(self.calendar_key):
            return self.data_unavailable_result("Calendar_agent.json")

        events = self.json_service.get_dataset(self.calendar_key)
        if not isinstance(events, list):
            return self.data_unavailable_result("Calendar_agent.json")

        query_lower = query.lower()

        # Find examination and calendar events matching query
        matched_events = []
        for evt in events:
            if not isinstance(evt, dict):
                continue
            name = str(evt.get("Event_Name", "")).lower()
            cat = str(evt.get("Category", "")).lower()
            desc = str(evt.get("Description", "")).lower()

            if any(term in query_lower for term in ["exam", "mid", "see", "test", "practical", "calendar"]) or \
               any(term in name or term in cat for term in query_lower.split() if len(term) > 3):
                matched_events.append(evt)

        if matched_events:
            lines = ["Examination & Calendar Details:"]
            for evt in matched_events[:6]:
                name = evt.get("Event_Name", "Event")
                start = evt.get("Start_Date", "")
                end = evt.get("End_Date", "")
                venue = evt.get("Venue", "")
                aud = evt.get("Audience", "")
                lines.append(f"• {name} ({aud}): {start} to {end} at {venue}")

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Academic Calendar & Examination Schedule",
                source_file="Calendar_agent.json",
                retrieval_method="filtered_json",
                records_matched=len(matched_events),
                filters={"query": query},
                relevance=0.92,
                verified=True
            )
            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.92,
                answer="\n".join(lines),
                data={"matched_count": len(matched_events), "events": matched_events[:6]},
                evidence=[ev]
            )

        default_answer = (
            "Standard Examination Schedule Structure:\n"
            "• Mid-1 Examinations: 8th week of semester instruction.\n"
            "• Mid-2 Examinations: 16th week of semester instruction.\n"
            "• Practical & Lab SEE Exams: Immediately following Mid-2.\n"
            "• Theory Semester End Exams (SEE): 2-week block post-practicals."
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.80,
            answer=default_answer,
            data={"status": "standard_exam_structure"},
            evidence=[]
        )
