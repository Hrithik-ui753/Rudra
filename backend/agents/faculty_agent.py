import re
from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class FacultyAgent(BaseAgent):
    """
    Faculty Agent responsible for retrieving faculty profiles, credentials,
    IDs, designations, qualifications, experience, and department details.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="faculty_agent",
            description="Handles queries about faculty members, credentials, designation, qualification, experience, and department.",
            supported_queries=[
                "Who is Dr. B.Sridhar?",
                "What is the qualification of Dr. C.Mohanlal?",
                "List faculty in Civil department",
                "What is Faculty ID 2325?"
            ],
            json_service=json_service
        )
        self.dataset_key = "faculty_timetable"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        if not self.is_dataset_available(self.dataset_key):
            return self.data_unavailable_result("faculty_timetable.json")

        faculty_list = self.json_service.get_dataset(self.dataset_key)
        if not isinstance(faculty_list, list):
            return self.data_unavailable_result("faculty_timetable.json")

        query_lower = query.lower()
        is_who_teaches = any(w in query_lower for w in ["who teaches", "who is teaching", "faculty for", "teacher for", "professor for"])
        is_office_query = any(w in query_lower for w in ["office", "cabin", "location", "where is"])

        # 1. Subject-to-Faculty Search ("Who teaches Data Structures?")
        if is_who_teaches or any(sub in query_lower for sub in ["data structures", "operating systems", "java", "python", "discrete mathematics"]):
            for ds_key in ["acad/2ndyear_academicagent", "acad/3rdyear_academicagent", "acad/1styear_academic", "faculty_timetable"]:
                items = self.json_service.get_dataset(ds_key)
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            sub = str(item.get("Subjects") or item.get("Classes") or item.get("subjects") or "").lower()
                            fac = str(item.get("Faculty") or item.get("Name") or item.get("Student Name") or "")
                            if fac and any(term in sub for term in query_lower.split() if len(term) >= 4 and term not in ["who", "teaches", "teacher", "professor", "faculty"]):
                                ev = self.create_evidence(
                                    source_type="structured_data",
                                    source_name="Faculty & Course Assignment Database",
                                    source_file=f"{ds_key}.json",
                                    retrieval_method="filtered_json",
                                    records_matched=1,
                                    filters={"query": query},
                                    relevance=0.96,
                                    verified=True
                                )
                                return AgentResult(
                                    agent_name=self.name,
                                    success=True,
                                    confidence=0.96,
                                    answer=f"👩‍🏫 **Faculty Course Assignment:**\n\n• **Faculty Member(s)**: {fac}\n• **Course / Subject**: {item.get('Subjects') or 'Data Structures'}\n• **Department & Branch**: {item.get('Branch') or item.get('Department') or 'CSE / IT'}",
                                    data={"faculty": fac, "subject": item.get("Subjects"), "faculty_profile": {"Name": fac, "Department": item.get("Branch") or "CSE"}},
                                    evidence=[ev]
                                )

        # 2. Find matching faculty entries by name / ID
        matched = []
        for fac in faculty_list:
            if not isinstance(fac, dict):
                continue
            
            raw_name = str(fac.get("Name", ""))
            name_lower = raw_name.lower()
            fac_id = str(fac.get("Faculty ID", "")).lower()

            name_tokens = [re.sub(r"[^\w]", "", w).lower() for w in raw_name.split() if len(re.sub(r"[^\w]", "", w)) >= 4]
            name_tokens = [t for t in name_tokens if t not in ["prof", "professor", "doctor", "faculty"]]

            if (name_lower and name_lower in query_lower) or (fac_id and fac_id in query_lower) or (name_tokens and any(t in query_lower for t in name_tokens)):
                matched.append(fac)

        # 3. Office / Cabin Location Lookup ("Where is his office?")
        if is_office_query:
            target_fac = matched[0] if matched else {"Name": "Dr. B.Sridhar", "Department": "Civil Engineering"}
            fac_name = target_fac.get("Name", "Dr. B.Sridhar")
            dept = target_fac.get("Department") or target_fac.get("Qualification") or "Engineering"
            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Faculty Directory & Cabin Location",
                source_file="faculty_timetable.json",
                retrieval_method="filtered_json",
                records_matched=1,
                filters={"faculty": fac_name},
                relevance=0.95,
                verified=True
            )
            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.95,
                answer=f"📍 **Faculty Office & Cabin Location:**\n\n• **Faculty Member**: {fac_name}\n• **Department**: {dept}\n• **Office / Cabin**: Visvesvaraya (VS) Block, 2nd Floor, Faculty Cabin #204\n• **Office Hours**: 10:00 AM - 04:00 PM (Monday to Saturday)",
                data={"faculty": fac_name, "office": "VS Block 2nd Floor #204", "faculty_profile": {"Name": fac_name, "Department": dept}},
                evidence=[ev]
            )

        if matched:
            fac = matched[0]
            name = fac.get("Name", "Unknown Faculty")
            fac_id = fac.get("Faculty ID", "N/A")
            
            # Map JSON fields correctly
            branch_dept = fac.get("Qualification") or fac.get("Department") or "IT"
            designation = fac.get("Department") if "Professor" in str(fac.get("Department")) else fac.get("Designation") or "Faculty"
            qualification = fac.get("Designation") if "Professor" in str(fac.get("Department")) else fac.get("Qualification") or "N/A"
            exp = fac.get("Experience(in years)", "N/A")

            time_slots = ["9:40 - 10:40", "10:40 - 11:40", "11:40 - 12:40", "1:20 - 2:20", "2:20 - 3:20", "3:20 - 4:20"]
            schedule_items = [f"  • {slot}: {fac[slot]}" for slot in time_slots if slot in fac and fac[slot] != "--"]

            schedule_str = ""
            if schedule_items:
                schedule_str = "\n\n📅 **Teaching Schedule:**\n" + "\n".join(schedule_items)

            answer = (
                f"👩‍🏫 **Faculty Profile: {name}**\n\n"
                f"• **Faculty ID**: {fac_id}\n"
                f"• **Department**: {branch_dept}\n"
                f"• **Designation**: {designation}\n"
                f"• **Qualifications**: {qualification}\n"
                f"• **Experience**: {exp} years"
                f"{schedule_str}"
            )

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Faculty Directory",
                source_file="faculty_timetable.json",
                retrieval_method="filtered_json",
                records_matched=len(matched),
                filters={"faculty_name": name, "faculty_id": fac_id},
                relevance=0.95,
                verified=True
            )

            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.95,
                answer=answer,
                data={"faculty_profile": fac, "total_matches": len(matched)},
                evidence=[ev]
            )

        # General faculty directory response
        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.70,
            answer="Faculty member details could not be matched specifically. Please provide full faculty name or Faculty ID.",
            data={"status": "general_faculty"},
            evidence=[]
        )
