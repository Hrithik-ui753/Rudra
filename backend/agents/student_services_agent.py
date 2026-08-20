from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class StudentServicesAgent(BaseAgent):
    """
    Student Services Agent responsible for administrative student services, bonafide certificates,
    leave requests, study certificates, circulars, and processing guidelines.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="student_services_agent",
            description="Handles administrative student services, Bonafide/Study certificates, leave applications, and circulars.",
            supported_queries=[
                "How do I get a Bonafide Certificate?",
                "How to apply for Leave Request?",
                "Where can I view academic circulars?",
                "What is the processing time for Study Certificate?"
            ],
            json_service=json_service
        )
        self.dataset_key = "student_services"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        if not self.is_dataset_available(self.dataset_key):
            return self.data_unavailable_result("student_services.json")

        services_data = self.json_service.get_dataset(self.dataset_key)
        if not isinstance(services_data, list):
            return self.data_unavailable_result("student_services.json")

        query_lower = query.lower()

        # Find matching student service
        matches = []
        for s in services_data:
            if not isinstance(s, dict):
                continue
            name = str(s.get("Service_Name", "")).lower()
            desc = str(s.get("Description", "")).lower()

            if (name and name in query_lower) or any(term in name for term in query_lower.split() if len(term) > 3):
                matches.append(s)

        if matches:
            s = matches[0]
            name = s.get("Service_Name", "Student Service")
            desc = s.get("Description", "N/A")
            docs = s.get("Required_Documents", "None")
            auth = s.get("Approval_Authority", "Academic Section")
            ptime = s.get("Processing_Time", "1-2 Days")
            fee = s.get("Fee", 0)

            answer = (
                f"Student Service: {name}\n"
                f"• Description: {desc}\n"
                f"• Required Documents: {docs}\n"
                f"• Approval Authority: {auth}\n"
                f"• Processing Time: {ptime}\n"
                f"• Service Fee: ₹{fee}"
            )

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Student Administrative Services Database",
                source_file="student_services.json",
                retrieval_method="filtered_json",
                records_matched=len(matches),
                filters={"service_name": name},
                relevance=0.95,
                verified=True
            )

            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.95,
                answer=answer,
                data={"service_details": s},
                evidence=[ev]
            )

        # Overview of available student services
        service_names = [s.get("Service_Name") for s in services_data if isinstance(s, dict) and s.get("Service_Name")]
        answer = (
            f"Available Student Administrative Services:\n"
            f"• Services: {', '.join(service_names[:6])}\n"
            f"• How to apply: Submit application via Student Portal or visit Academic Section counter."
        )

        ev = self.create_evidence(
            source_type="structured_data",
            source_name="Student Administrative Services Database",
            source_file="student_services.json",
            retrieval_method="structured_json",
            records_matched=len(services_data),
            filters={"query": query},
            relevance=0.85,
            verified=True
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.85,
            answer=answer,
            data={"available_services": service_names},
            evidence=[ev]
        )
