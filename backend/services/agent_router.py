import json
import re
from typing import List, Optional, Tuple, Dict, Any
from models.schemas import RoutingDecision
from utils.logger import logger
from services.llm_service import LLMService


VALID_REGISTERED_AGENTS = [
    "academic_agent",
    "faculty_agent",
    "timetable_agent",
    "examination_agent",
    "placement_agent",
    "scholarship_agent",
    "infrastructure_agent",
    "student_services_agent",
    "transport_agent",
    "library_agent",
    "clubs_agent",
    "events_agent",
]



class AgentRouter:
    """
    Intelligent routing service for analyzing user queries and determining
    the target agent(s) required to fulfill the request.
    Supports multi-agent routing, Gemini LLM classification, and structured Pydantic validation.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service

        # Intent keyword mapping patterns (Order matters: specific rules first)
        self.keyword_rules = [
            # Direct Roll Number Search
            (
                r"\b1602[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{3}\b",
                "academic_agent",
                0.98
            ),
            # Events & Activities Agent (Prioritized to handle event typos & discovery queries)
            (
                r"\b(event|events|eevent|eevnts|upcomig|upcominh|hackathon|hackathons|hackthon|hackthons|workshop|workshops|seminar|seminars|guest lecture|guest talk|webinar|conclave|fest|orientation|competition|competitions|upcoming|upcoming tech|tech events|in hyderabad|register event|registration deadline|open registration|free events|add to calendar|microsoft calendar|registered for|my events|reminders|reminder|next event|coming up next|events tomorrow)\b",
                "events_agent",
                0.92
            ),
            # Faculty Agent & Who Teaches / Office queries
            (
                r"\b(faculty|professor|prof|teacher|lecturer|dr\.|dr\b|doctor|hod|qualification|experience|designation|mam|madam|sir|ms\.|ms\b|mrs\.|mrs\b|miss|who teaches|who is teaching|faculty for|teacher for|professor for|office|cabin|where is his office|where is her office|hod office|faculty office)\b",
                "faculty_agent",
                0.90
            ),
            # Academic Agent
            (
                r"\b(subject|subjects|course|courses|syllabus|credit|credits|sem|semester|cgpa|sgpa|gpa|backlog|backlogs|grade|grades|regulation|regulations|curriculum|unit|branch|civil|cse|it\s+dept|it\s+department|it\s+branch|ece|eee|mech)\b",
                "academic_agent",
                0.85
            ),
            # Timetable Agent
            (
                r"\b(class|classes|schedule|schedules|timetable|time|slot|teaching|room|period|lab schedule|09:40|10:40|11:40|1:20|2:20|3:20)\b",
                "timetable_agent",
                0.85
            ),
            # Examination Agent
            (
                r"\b(exam|exams|examination|mid|mid1|mid2|see|practical|practicals|eval|test|tests|result|results|hall ticket|timetable exam|calendar exam)\b",
                "examination_agent",
                0.85
            ),
            # Placement Agent
            (
                r"\b(placement|placements|company|companies|package|salary|lpa|ctc|recruitment|recruiters|interview|job|internship|hiring|flipkart|servicenow|visa|resume|eligibility)\b",
                "placement_agent",
                0.85
            ),
            # Scholarship Agent
            (
                r"\b(scholarship|scholarships|fee|fees|reimbursement|epass|ts epass|tuition|fine|fines|dues|instalment|installment)\b",
                "scholarship_agent",
                0.85
            ),
            # Infrastructure Agent
            (
                r"\b(infrastructure|facility|facilities|building|campus|lab|auditorium|canteen|wifi|hostel|playground|gym|hall|vs block)\b",
                "infrastructure_agent",
                0.80
            ),
            # Transport Agent
            (
                r"\b(bus|transport|route|stop|stops|driver|ecil|malkajgiri|lb nagar|mehdipatnam|vehicle|boarding)\b",
                "transport_agent",
                0.90
            ),
            # Library Agent
            (
                r"\b(library|book|books|author|isbn|borrow|return|issue|journal|volume|vol)\b",
                "library_agent",
                0.90
            ),
            # Clubs Agent
            (
                r"\b(club|clubs|rangmanch|euphoria|cultural|dance|singing|robotics|ieee|nss|activity)\b",
                "clubs_agent",
                0.85
            ),
            # Student Services Agent
            (
                r"\b(student service|service|circular|circulars|leave|bonafide|study certificate|certificate|certificates|approval|authority|form|admin)\b",
                "student_services_agent",
                0.85
            ),
        ]



    def route_decision(self, query: str, registered_agent_names: Optional[List[str]] = None) -> RoutingDecision:
        """
        Analyzes user query and returns a structured RoutingDecision Pydantic object.
        Used by the LangGraph Orchestrator.
        """
        allowed = registered_agent_names or VALID_REGISTERED_AGENTS
        clean_query = query.strip()

        if not clean_query:
            return RoutingDecision(
                agents=["academic_agent"],
                reason="Empty query defaulted to academic_agent",
                confidence=0.0
            )

        # First, check if LLM is available for intelligent routing
        if self.llm_service and self.llm_service.is_available():
            llm_decision = self._classify_with_llm_structured(clean_query, allowed)
            if llm_decision and llm_decision.agents:
                logger.info(f"LLM Routing Decision for '{clean_query[:40]}...': {llm_decision.agents} (conf: {llm_decision.confidence})")
                return llm_decision

        # Keyword & pattern rules fallback
        matched_agents = []
        highest_conf = 0.0
        clean_lower = clean_query.lower()

        for pattern, agent_name, base_conf in self.keyword_rules:
            if agent_name in allowed and re.search(pattern, clean_lower, re.IGNORECASE):
                if agent_name not in matched_agents:
                    matched_agents.append(agent_name)
                highest_conf = max(highest_conf, base_conf)

        # Multi-agent combination detection
        is_faculty = any(k in clean_lower for k in ["faculty", "prof", "dr.", "doctor", "teacher", "who teaches", "who is teaching", "mam", "madam", "sir", "ms.", "ms ", "mrs", "miss"])
        is_schedule = any(k in clean_lower for k in ["teaching", "where is", "class", "at 10:", "at 11:", "at 1:", "at 2:", "at 3:", "schedule", "timetable", "when is"])
        is_subject = any(k in clean_lower for k in ["subject", "course", "data structures", "dbms", "os", "ai", "ml", "sem", "semester"])

        if is_faculty and (is_schedule or is_subject):
            for a in ["faculty_agent", "timetable_agent", "academic_agent"]:
                if a in allowed and a not in matched_agents:
                    matched_agents.append(a)
            highest_conf = max(highest_conf, 0.92)

        if not matched_agents:
            matched_agents = ["academic_agent"] if "academic_agent" in allowed else [allowed[0]]
            highest_conf = 0.50

        logger.info(f"Rule Routing Decision for '{clean_query[:40]}...': {matched_agents} (conf: {highest_conf})")
        return RoutingDecision(
            agents=matched_agents,
            reason=f"Keyword matching selected: {', '.join(matched_agents)}",
            confidence=highest_conf
        )

    def route_query(self, query: str) -> Tuple[List[str], float]:
        """
        Backward-compatible route query method returning (agents_list, confidence_score).
        """
        decision = self.route_decision(query)
        return decision.agents, decision.confidence

    def _classify_with_llm_structured(self, query: str, allowed_agents: List[str]) -> Optional[RoutingDecision]:
        """
        Uses Gemini LLM to classify user query into structured JSON format selecting ONLY from allowed_agents.
        """
        prompt = (
            f"You are the query router for a campus multi-agent system. "
            f"Allowed agents: {json.dumps(allowed_agents)}\n\n"
            f"Analyze this student/faculty query: \"{query}\"\n"
            f"Return JSON matching this exact schema:\n"
            f"{{\n"
            f"  \"agents\": [\"agent_name_1\", \"agent_name_2\"],\n"
            f"  \"reason\": \"brief explanation of routing choice\",\n"
            f"  \"confidence\": 0.95\n"
            f"}}\n"
            f"RULES:\n"
            f"1. ONLY select agent names from the allowed agents list.\n"
            f"2. If the query requires multiple agents (e.g., faculty + schedule), include ALL relevant agents.\n"
            f"3. Return raw JSON string only, without markdown formatting."
        )

        resp = self.llm_service.generate(prompt)
        if not resp:
            return None

        try:
            # Clean markdown codeblocks if present
            clean_resp = resp.strip()
            if clean_resp.startswith("```"):
                clean_resp = clean_resp.split("```")[1]
                if clean_resp.startswith("json"):
                    clean_resp = clean_resp[4:].strip()
            
            data = json.loads(clean_resp)
            if isinstance(data, dict) and "agents" in data:
                raw_agents = data.get("agents", [])
                valid_agents = [a for a in raw_agents if a in allowed_agents]
                if valid_agents:
                    return RoutingDecision(
                        agents=valid_agents,
                        reason=str(data.get("reason", "LLM routing classification")),
                        confidence=float(data.get("confidence", 0.90))
                    )
        except Exception as e:
            logger.warning(f"Failed to parse LLM router JSON output '{resp}': {e}")

        return None

