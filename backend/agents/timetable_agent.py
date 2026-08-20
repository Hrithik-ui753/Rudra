import re
from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class TimetableAgent(BaseAgent):
    """
    Timetable Agent responsible for retrieving class schedules, faculty schedules,
    time-slot queries, and room/lab schedule information.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="timetable_agent",
            description="Handles queries about class schedules, time slots, faculty teaching schedules, and lab schedules.",
            supported_queries=[
                "What class is at 10:40?",
                "Where is Dr. B.Sridhar teaching at 10:40?",
                "Show schedule for Civil 2nd year",
                "What is the schedule for 11:40?"
            ],
            json_service=json_service
        )
        self.dataset_key = "faculty_timetable"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        if not self.is_dataset_available(self.dataset_key):
            return self.data_unavailable_result("faculty_timetable.json")

        timetable_data = self.json_service.get_dataset(self.dataset_key)
        if not isinstance(timetable_data, list):
            return self.data_unavailable_result("faculty_timetable.json")

        query_lower = query.lower()

        # Identify time slot if present in query (e.g. 9:40, 10:40, 11:40, 1:20, 2:20, 3:20)
        time_slots = ["9:40 - 10:40", "10:40 - 11:40", "11:40 - 12:40", "1:20 - 2:20", "2:20 - 3:20", "3:20 - 4:20"]
        requested_slot = None
        for slot in time_slots:
            time_part = slot.split(" - ")[0]
            if time_part in query_lower:
                requested_slot = slot
                break

        # Check for faculty match
        matching_faculty = []
        for fac in timetable_data:
            if not isinstance(fac, dict):
                continue
            name = str(fac.get("Name", "")).lower()
            if name and (name in query_lower or any(t in query_lower for t in name.split() if len(t) > 3)):
                matching_faculty.append(fac)

        if matching_faculty:
            fac = matching_faculty[0]
            fac_name = fac.get("Name", "Faculty")
            if requested_slot and requested_slot in fac:
                assigned_class = fac[requested_slot]
                answer = f"At {requested_slot}, {fac_name} is assigned to: {assigned_class}."
            else:
                schedule_lines = [f"Teaching schedule for {fac_name}:"]
                for slot in time_slots:
                    if slot in fac:
                        schedule_lines.append(f"• {slot}: {fac[slot]}")
                answer = "\n".join(schedule_lines)

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Faculty Timetable",
                source_file="faculty_timetable.json",
                retrieval_method="filtered_json",
                records_matched=1,
                filters={"faculty": fac_name, "time_slot": requested_slot} if requested_slot else {"faculty": fac_name},
                relevance=0.95,
                verified=True
            )

            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.95,
                answer=answer,
                data={"faculty": fac_name, "schedule": fac},
                evidence=[ev]
            )

        # Slot-specific search across all faculty
        if requested_slot:
            active_classes = []
            for fac in timetable_data:
                if isinstance(fac, dict) and requested_slot in fac:
                    c_info = fac[requested_slot]
                    if c_info and c_info != "--":
                        active_classes.append(f"• {fac.get('Name')}: {c_info}")

            if active_classes:
                ev = self.create_evidence(
                    source_type="structured_data",
                    source_name="Faculty Timetable",
                    source_file="faculty_timetable.json",
                    retrieval_method="filtered_json",
                    records_matched=len(active_classes),
                    filters={"time_slot": requested_slot},
                    relevance=0.90,
                    verified=True
                )
                answer = f"Classes scheduled at {requested_slot}:\n" + "\n".join(active_classes[:10])
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    confidence=0.90,
                    answer=answer,
                    data={"slot": requested_slot, "active_count": len(active_classes)},
                    evidence=[ev]
                )

        # General timetable fallback summary
        default_answer = (
            "Standard Campus Timetable Slots:\n"
            "• Period 1: 09:40 AM - 10:40 AM\n"
            "• Period 2: 10:40 AM - 11:40 AM\n"
            "• Period 3: 11:40 AM - 12:40 PM\n"
            "• Lunch Break: 12:40 PM - 01:20 PM\n"
            "• Period 4: 01:20 PM - 02:20 PM\n"
            "• Lab Period 1: 02:20 PM - 03:20 PM\n"
            "• Lab Period 2: 03:20 PM - 04:20 PM"
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.80,
            answer=default_answer,
            data={"status": "standard_slots"},
            evidence=[]
        )
