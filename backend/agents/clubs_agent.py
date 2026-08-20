from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class ClubsAgent(BaseAgent):
    """
    Clubs Agent responsible for student extra-curricular clubs, technical societies,
    cultural clubs (Rangmanch), registration forms, eligibility, and events.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="clubs_agent",
            description="Handles student clubs, cultural societies (Rangmanch), technical clubs, registrations, and club events.",
            supported_queries=[
                "Tell me about Rangmanch club",
                "What student clubs are available?",
                "How to register for Theme Ballet club?",
                "What is the venue for cultural clubs?"
            ],
            json_service=json_service
        )
        self.dataset_key = "VCE_clubs_simplified"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        if not self.is_dataset_available(self.dataset_key):
            return self.data_unavailable_result("VCE_clubs_simplified.json")

        clubs = self.json_service.get_dataset(self.dataset_key)
        if not isinstance(clubs, list):
            return self.data_unavailable_result("VCE_clubs_simplified.json")

        query_lower = query.lower()

        # Find matching student club
        matched = []
        for c in clubs:
            if not isinstance(c, dict):
                continue
            name = str(c.get("Club_Name", "")).lower()
            cat = str(c.get("Category", "")).lower()
            subcat = str(c.get("Subcategory", "")).lower()

            if (name and name in query_lower) or any(term in name for term in query_lower.split() if len(term) > 3):
                matched.append(c)

        if matched:
            c = matched[0]
            name = c.get("Club_Name", "Student Club")
            cat = c.get("Category", "N/A")
            desc = c.get("Description", "N/A")
            venue = c.get("Venue", "Campus Hub")
            mem = c.get("Membership", "Open")
            event = c.get("Major_Event", "Annual Fest")

            answer = (
                f"Student Club Details ({name}):\n"
                f"• Category: {cat}\n"
                f"• Description: {desc}\n"
                f"• Venue: {venue}\n"
                f"• Membership: {mem}\n"
                f"• Major Event: {event}"
            )

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Student Clubs Directory",
                source_file="VCE_clubs_simplified.json",
                retrieval_method="filtered_json",
                records_matched=len(matched),
                filters={"club_name": name},
                relevance=0.95,
                verified=True
            )
            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.95,
                answer=answer,
                data={"club_details": c},
                evidence=[ev]
            )

        # General clubs overview
        club_names = [c.get("Club_Name") for c in clubs if isinstance(c, dict) and c.get("Club_Name")]
        answer = (
            f"Active Campus Student Clubs:\n"
            f"• Cultural & Technical Clubs: {', '.join(club_names[:6])}\n"
            f"• Registration: Open for 1st-4th Year students via Google Form / Auditions."
        )

        ev = self.create_evidence(
            source_type="structured_data",
            source_name="Student Clubs Directory",
            source_file="VCE_clubs_simplified.json",
            retrieval_method="structured_json",
            records_matched=len(clubs),
            filters={"query": query},
            relevance=0.85,
            verified=True
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.85,
            answer=answer,
            data={"total_clubs": len(clubs)},
            evidence=[ev]
        )
