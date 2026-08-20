from typing import List, Dict, Any, Optional
from agents.base_agent import BaseAgent
from models.schemas import AgentResult
from services.json_service import JSONDataService
from utils.logger import logger


class TransportAgent(BaseAgent):
    """
    Transport Agent responsible for campus bus schedules, route numbers, boarding stops,
    timings, drivers, and transport fees.
    """

    def __init__(self, json_service: JSONDataService):
        super().__init__(
            name="transport_agent",
            description="Handles campus bus routes, stops, route numbers, timings, drivers, and bus transport fees.",
            supported_queries=[
                "Which bus goes to ECIL?",
                "What is Route No 11?",
                "What time does the bus start in the morning?",
                "What is the transport fee?"
            ],
            json_service=json_service
        )
        self.dataset_key = "transport"

    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        logger.info(f"[{self.name}] Processing query: '{query}'")

        if not self.is_dataset_available(self.dataset_key):
            return self.data_unavailable_result("transport.json")

        buses = self.json_service.get_dataset(self.dataset_key)
        if not isinstance(buses, list):
            return self.data_unavailable_result("transport.json")

        query_lower = query.lower()

        # Find matching bus routes
        matched = []
        for bus in buses:
            if not isinstance(bus, dict):
                continue
            r_name = str(bus.get("Route_Name", "")).lower()
            stops = str(bus.get("Stops", "")).lower()
            r_no = str(bus.get("Route_No", ""))

            if (r_name and r_name in query_lower) or (r_no and r_no in query_lower) or any(term in stops for term in query_lower.split() if len(term) > 3):
                matched.append(bus)

        if matched:
            bus = matched[0]
            r_no = bus.get("Route_No", "N/A")
            r_name = bus.get("Route_Name", "Route")
            m_time = bus.get("Morning_Start_Time", "07:45 AM")
            e_time = bus.get("Evening_Start_Time", "04:35 PM")
            driver = bus.get("Driver_Name", "N/A")
            fee = bus.get("Transport_Fee", 37000)
            stops = bus.get("Stops", "")

            answer = (
                f"Bus Transport Info (Route No {r_no} - {r_name}):\n"
                f"• Morning Departure: {m_time}\n"
                f"• Evening Return: {e_time}\n"
                f"• Driver: {driver}\n"
                f"• Transport Fee: ₹{fee}/year\n"
                f"• Key Stops: {stops[:150]}..."
            )

            ev = self.create_evidence(
                source_type="structured_data",
                source_name="Bus Transport Database",
                source_file="transport.json",
                retrieval_method="filtered_json",
                records_matched=len(matched),
                filters={"route_no": r_no, "route_name": r_name},
                relevance=0.95,
                verified=True
            )

            return AgentResult(
                agent_name=self.name,
                success=True,
                confidence=0.95,
                answer=answer,
                data={"bus_details": bus},
                evidence=[ev]
            )

        # Overview of transport system
        routes = [f"Route {b.get('Route_No')}: {b.get('Route_Name')}" for b in buses[:5] if isinstance(b, dict)]
        answer = (
            f"Campus Bus Transport System:\n"
            f"• Major Routes: {', '.join(routes)}\n"
            f"• Standard Start Time: 07:45 AM - 08:00 AM\n"
            f"• Transport Fee: ₹37,000 per annum."
        )

        ev = self.create_evidence(
            source_type="structured_data",
            source_name="Bus Transport Database",
            source_file="transport.json",
            retrieval_method="structured_json",
            records_matched=len(buses),
            filters={"query": query},
            relevance=0.85,
            verified=True
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            confidence=0.85,
            answer=answer,
            data={"total_routes": len(buses)},
            evidence=[ev]
        )
