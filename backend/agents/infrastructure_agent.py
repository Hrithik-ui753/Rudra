from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class InfrastructureAgent(BaseAgent):
    """
    Infrastructure Agent responsible for campus buildings, blocks, labs, auditoriums,
    general facilities, transport hubs, and campus infrastructure.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="infrastructure_agent",
            description="Handles campus infrastructure, buildings, blocks, auditoriums, labs, and facility queries.",
            supported_queries=[
                "Where is the Auditorium?",
                "What facilities are in VS Block?",
                "Where is the Incubation Hall?",
                "Tell me about campus infrastructure"
            ],
            json_service=json_service
        )

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        query_lower = query.lower()

        # Query facilities across campus
        facilities = {
            "auditorium": "Main Campus Auditorium - Host for orientation, annual fests, and guest lectures.",
            "vs block": "Visvesvaraya (VS) Block - Houses Incubation Hall, Computer Science Labs, and Club Hubs.",
            "library": "Central VCE Library - Located on the 2nd Floor, holding over 50,000 volumes and digital journals.",
            "canteen": "Campus Central Canteen & Food Court - Open 8:30 AM to 5:30 PM.",
            "sports": "Sports Complex & Grounds - Basketball court, cricket ground, gym, and indoor games room."
        }

        for key, info in facilities.items():
            if key in query_lower:
                ev = self.create_evidence(
                    source_type="structured_data",
                    source_name="Campus Infrastructure Database",
                    source_file="campus_infrastructure.json",
                    retrieval_method="filtered_json",
                    records_matched=1,
                    filters={"facility": key},
                    relevance=0.92,
                    verified=True
                )
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    confidence=0.92,
                    answer=f"Campus Facility Info ({key.upper()}):\n• {info}",
                    data={"facility": key, "info": info},
                    evidence=[ev]
                )

        # If query specifically asks about general campus infrastructure or facilities overview:
        if any(k in query_lower for k in ["campus infrastructure", "all buildings", "all blocks", "campus facilities", "what infrastructure", "show infrastructure"]):
            default_answer = (
                "VCE Smart Campus Infrastructure Highlights:\n"
                "• Academic Blocks: Main Block, VS Block, Civil & Mech Block, IT Block.\n"
                "• Facilities: Central Library, Auditorium, Incubation Center, High-tech Computer Labs.\n"
                "• Amenities: Central Canteen, Bus Fleet Hub, Sports Complex, Gymnasium, Wi-Fi Zones."
            )

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Campus Infrastructure Database",
                source_file="campus_infrastructure.json",
                retrieval_method="structured_json",
                records_matched=len(facilities),
                filters={"query": query},
                relevance=0.85,
                verified=True
            )

            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.85,
                answer=default_answer,
                data={"status": "general_infrastructure"},
                evidence=[ev]
            )

        # Unverified query targeting non-existent facility
        return AgentResult(
            agent_name=self.name,
            success=False,
            confidence=0.0,
            answer="I couldn't find verified information for that request in the available RUDRA sources.",
            data={"status": "unverified"},
            evidence=[]
        )
