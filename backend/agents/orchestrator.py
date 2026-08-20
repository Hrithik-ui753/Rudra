import asyncio
import time
from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, START, END

from models.schemas import AgentResult, ChatResponse, AgentInfo, RoutingDecision, Evidence
from services.json_service import JSONDataService
from services.llm_service import LLMService
from services.agent_router import AgentRouter
from services.context_service import ConversationContextService
from services.rag_service import RAGService
from utils.logger import logger

from agents.academic_agent import AcademicAgent
from agents.faculty_agent import FacultyAgent
from agents.timetable_agent import TimetableAgent
from agents.examination_agent import ExaminationAgent
from agents.placement_agent import PlacementAgent
from agents.scholarship_agent import ScholarshipAgent
from agents.infrastructure_agent import InfrastructureAgent
from agents.student_services_agent import StudentServicesAgent
from agents.transport_agent import TransportAgent
from agents.library_agent import LibraryAgent
from agents.clubs_agent import ClubsAgent
from agents.events_agent import EventsAgent


class OrchestratorState(TypedDict, total=False):
    user_id: str
    conversation_id: str
    query: str
    resolved_query: str
    context_used: bool
    needs_clarification: bool
    clarification_message: str
    intent: str
    selected_agents: List[str]
    agent_results: Dict[str, Any]
    final_answer: str
    confidence: float
    sources: List[str]
    evidence: List[Evidence]
    errors: List[str]
    start_time: float
    total_time: float


class OrchestratorAgent:
    """
    LangGraph-powered Central Orchestrator Agent for RUDRA Smart Campus AI System.
    Manages intent understanding, context resolution, agent routing, concurrent execution,
    result validation, and Gemini LLM response synthesis via a state graph architecture.
    """

    def __init__(
        self,
        json_service: JSONDataService,
        llm_service: Optional[LLMService] = None,
        rag_service: Optional[RAGService] = None
    ):
        self.json_service = json_service
        self.llm_service = llm_service or LLMService()
        self.rag_service = rag_service
        self.router = AgentRouter(llm_service=self.llm_service)
        self.context_service = ConversationContextService()

        # Central Agent Registry
        self.agents: Dict[str, Any] = {
            "academic_agent": AcademicAgent(self.json_service),
            "faculty_agent": FacultyAgent(self.json_service),
            "timetable_agent": TimetableAgent(self.json_service),
            "examination_agent": ExaminationAgent(self.json_service),
            "placement_agent": PlacementAgent(self.json_service),
            "scholarship_agent": ScholarshipAgent(self.json_service),
            "infrastructure_agent": InfrastructureAgent(self.json_service),
            "student_services_agent": StudentServicesAgent(self.json_service),
            "transport_agent": TransportAgent(self.json_service),
            "library_agent": LibraryAgent(self.json_service),
            "clubs_agent": ClubsAgent(self.json_service),
            "events_agent": EventsAgent(self.json_service),
        }
        logger.info(f"OrchestratorAgent initialized with {len(self.agents)} registered specialized agents.")

        # Build LangGraph StateGraph Execution Pipeline
        self.graph = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph state graph workflow."""
        workflow = StateGraph(OrchestratorState)

        workflow.add_node("resolve_context", self._resolve_context_node)
        workflow.add_node("route", self._route_node)
        workflow.add_node("execute_agents", self._execute_agents_node)
        workflow.add_node("synthesize", self._synthesize_node)
        workflow.add_node("update_context", self._update_context_node)

        workflow.add_edge(START, "resolve_context")
        workflow.add_edge("resolve_context", "route")
        workflow.add_edge("route", "execute_agents")
        workflow.add_edge("execute_agents", "synthesize")
        workflow.add_edge("synthesize", "update_context")
        workflow.add_edge("update_context", END)

        return workflow.compile()

    def _resolve_context_node(self, state: OrchestratorState) -> OrchestratorState:
        """LangGraph Node: Resolve references and entities from conversation context."""
        query = state.get("query", "").strip()
        user_id = state.get("user_id", "user_guest")
        conversation_id = state.get("conversation_id", "default_session")

        resolved_query, context_used, needs_clarification, clarification_msg = self.context_service.resolve_context(
            user_id, conversation_id, query
        )

        state["resolved_query"] = resolved_query
        state["context_used"] = context_used
        state["needs_clarification"] = needs_clarification
        state["clarification_message"] = clarification_msg or ""
        return state

    def _route_node(self, state: OrchestratorState) -> OrchestratorState:
        """LangGraph Node: Intent classification & agent selection."""
        if state.get("needs_clarification"):
            state["selected_agents"] = []
            state["confidence"] = 0.5
            state["intent"] = "Ambiguity Clarification"
            return state

        query_to_use = state.get("resolved_query") or state.get("query", "").strip()
        if not query_to_use:
            state["selected_agents"] = []
            state["confidence"] = 0.0
            state["intent"] = "Empty Query"
            return state

        registered_keys = list(self.agents.keys())
        routing_decision: RoutingDecision = self.router.route_decision(query_to_use, registered_keys)

        state["selected_agents"] = routing_decision.agents
        state["confidence"] = routing_decision.confidence
        state["intent"] = routing_decision.reason
        logger.info(f"[LangGraph:Route] Selected agents: {routing_decision.agents} for resolved query: '{query_to_use[:40]}...'")
        return state

    def _execute_agent_sync(self, agent_name: str, query: str) -> Optional[AgentResult]:
        """Synchronously execute a single agent safely with error catching."""
        agent = self.agents.get(agent_name)
        if not agent:
            return None
        try:
            return agent.process(query)
        except Exception as e:
            logger.error(f"Execution error in agent '{agent_name}': {e}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                confidence=0.0,
                answer=f"Agent '{agent_name}' encountered an error during execution.",
                error=str(e),
                evidence=[]
            )

    def _execute_agents_node(self, state: OrchestratorState) -> OrchestratorState:
        """LangGraph Node: Execute selected agents."""
        if state.get("needs_clarification"):
            state["agent_results"] = {}
            state["errors"] = []
            state["sources"] = []
            state["evidence"] = []
            return state

        selected_agents = state.get("selected_agents", [])
        query_to_use = state.get("resolved_query") or state.get("query", "")
        agent_results = {}
        errors = []
        sources = []
        evidence_list = []

        if not selected_agents:
            state["agent_results"] = {}
            state["errors"] = ["No agent was selected for this query."]
            state["sources"] = []
            state["evidence"] = []
            return state

        # Execute agents
        for agent_name in selected_agents:
            res = self._execute_agent_sync(agent_name, query_to_use)
            if res:
                agent_results[agent_name] = res
                if not res.success and res.error:
                    errors.append(f"{agent_name}: {res.error}")
                # Track evidence objects
                if hasattr(res, "evidence") and isinstance(res.evidence, list):
                    evidence_list.extend(res.evidence)
                # Track data sources if present
                if hasattr(res, "data") and isinstance(res.data, dict):
                    dataset_name = res.data.get("dataset")
                    if dataset_name and dataset_name not in sources:
                        sources.append(dataset_name)

        state["agent_results"] = agent_results
        state["errors"] = errors
        state["sources"] = sources
        state["evidence"] = evidence_list
        logger.info(f"[LangGraph:Execute] Executed {len(agent_results)} agents with {len(evidence_list)} evidence objects.")
        return state

    def _synthesize_node(self, state: OrchestratorState) -> OrchestratorState:
        """LangGraph Node: Synthesize final answer via Gemini LLM or fallback with verification check."""
        if state.get("needs_clarification"):
            state["final_answer"] = state.get("clarification_message", "Could you please clarify your request?")
            state["confidence"] = 0.5
            return state

        query = state.get("resolved_query") or state.get("query", "")
        agent_results = state.get("agent_results", {})
        evidence_list = state.get("evidence", [])

        if not agent_results:
            state["final_answer"] = "I couldn't find verified information for that request in the available RUDRA sources."
            state["confidence"] = 0.0
            return state

        # Verification Rule Check:
        # Check if any verified evidence with matched records > 0 was retrieved
        valid_evidence = [e for e in evidence_list if e.verified and e.records_matched > 0]
        if not valid_evidence:
            state["final_answer"] = "I couldn't find verified information for that request in the available RUDRA sources."
            state["confidence"] = 0.0
            return state

        final_answer = self.llm_service.synthesize_answer(query, agent_results)
        state["final_answer"] = final_answer
        return state

    def _update_context_node(self, state: OrchestratorState) -> OrchestratorState:
        """LangGraph Node: Save updated context turn data after response synthesis."""
        if not state.get("needs_clarification"):
            user_id = state.get("user_id", "user_guest")
            conversation_id = state.get("conversation_id", "default_session")
            query = state.get("query", "")
            agents_used = state.get("selected_agents", [])
            agent_results = state.get("agent_results", {})
            final_answer = state.get("final_answer", "")

            self.context_service.update_context(
                user_id=user_id,
                conversation_id=conversation_id,
                query=query,
                agents_used=agents_used,
                agent_results=agent_results,
                final_answer=final_answer
            )
        return state

    async def _execute_agents_node_async(self, state: OrchestratorState) -> OrchestratorState:
        """Async version of agent execution node running agents concurrently using asyncio.to_thread with timeout."""
        if state.get("needs_clarification"):
            state["agent_results"] = {}
            state["errors"] = []
            state["sources"] = []
            state["evidence"] = []
            return state

        selected_agents = state.get("selected_agents", [])
        query_to_use = state.get("resolved_query") or state.get("query", "")
        agent_results = {}
        errors = []
        sources = []
        evidence_list = []

        if not selected_agents:
            state["agent_results"] = {}
            state["errors"] = ["No agent was selected for this query."]
            state["sources"] = []
            state["evidence"] = []
            return state

        async def run_single_agent(name: str):
            agent = self.agents.get(name)
            if not agent:
                return name, None
            try:
                res = await asyncio.wait_for(
                    asyncio.to_thread(agent.process, query_to_use),
                    timeout=5.0
                )
                return name, res
            except asyncio.TimeoutError:
                logger.error(f"Agent '{name}' timed out after 5 seconds.")
                return name, AgentResult(
                    agent_name=name,
                    success=False,
                    confidence=0.0,
                    answer=f"Agent '{name}' request timed out.",
                    error="Timeout",
                    evidence=[]
                )
            except Exception as e:
                logger.error(f"Error running agent '{name}': {e}")
                return name, AgentResult(
                    agent_name=name,
                    success=False,
                    confidence=0.0,
                    answer=f"Agent '{name}' failed.",
                    error=str(e),
                    evidence=[]
                )

        tasks = [run_single_agent(name) for name in selected_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for item in results:
            if isinstance(item, tuple) and len(item) == 2:
                name, res = item
                if res:
                    agent_results[name] = res
                    if not res.success and res.error:
                        errors.append(f"{name}: {res.error}")
                    if hasattr(res, "evidence") and isinstance(res.evidence, list):
                        evidence_list.extend(res.evidence)
                    if hasattr(res, "data") and isinstance(res.data, dict):
                        dataset = res.data.get("dataset")
                        if dataset and dataset not in sources:
                            sources.append(dataset)

        # Retrieve ChromaDB Vector Embeddings & RAG Chunks if rag_service is available
        if self.rag_service:
            try:
                chroma_ev = await asyncio.to_thread(self.rag_service.search_as_evidence, query_to_use, 2)
                if chroma_ev:
                    evidence_list.extend(chroma_ev)
                    if "ChromaDB RAG Vector Store" not in sources:
                        sources.append("ChromaDB RAG Vector Store")
            except Exception as e:
                logger.error(f"[Orchestrator] Error running ChromaDB vector search: {e}")

        state["agent_results"] = agent_results
        state["errors"] = errors
        state["sources"] = sources
        state["evidence"] = evidence_list
        return state

    def process_query(self, query: str, user_id: str = "user_guest", conversation_id: str = "default_session") -> ChatResponse:
        """
        Synchronous entrypoint to execute full orchestration graph with context resolution.
        """
        start_time = time.time()
        query_str = query.strip()

        if not query_str:
            return ChatResponse(
                success=False,
                message="Please provide a valid query.",
                agents_used=[],
                confidence=0.0,
                sources=[],
                evidence=[],
                context_used=False,
                metadata={"execution_time_seconds": 0.0}
            )

        initial_state: OrchestratorState = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query": query_str,
            "resolved_query": query_str,
            "context_used": False,
            "needs_clarification": False,
            "clarification_message": "",
            "intent": "",
            "selected_agents": [],
            "agent_results": {},
            "final_answer": "",
            "confidence": 0.0,
            "sources": [],
            "evidence": [],
            "errors": [],
            "start_time": start_time
        }

        # Invoke LangGraph compiled pipeline
        final_state = self.graph.invoke(initial_state)
        total_time = round(time.time() - start_time, 4)

        agents_used = final_state.get("selected_agents", [])
        primary_agent = agents_used[0] if agents_used else "academic_agent"
        agent_results = final_state.get("agent_results", {})
        evidence_list = final_state.get("evidence", [])

        raw_data = {
            name: res.model_dump() if hasattr(res, "model_dump") else str(res)
            for name, res in agent_results.items()
        }

        return ChatResponse(
            success=len(agents_used) > 0 or final_state.get("needs_clarification", False),
            message=final_state.get("final_answer", "No response generated."),
            response=final_state.get("final_answer", "No response generated."),
            agents_used=agents_used,
            agent_name=primary_agent,
            confidence=final_state.get("confidence", 0.0),
            sources=final_state.get("sources", []),
            evidence=evidence_list,
            context_used=final_state.get("context_used", False),
            raw_data=raw_data,
            metadata={
                "intent": final_state.get("intent", ""),
                "resolved_query": final_state.get("resolved_query", query_str),
                "execution_time_seconds": total_time,
                "errors": final_state.get("errors", [])
            }
        )

    async def process_query_async(self, query: str, user_id: str = "user_guest", conversation_id: str = "default_session") -> ChatResponse:
        """
        Asynchronous entrypoint using context resolution, non-blocking agent execution, and LangGraph pipeline.
        """
        start_time = time.time()
        query_str = query.strip()

        if not query_str:
            return ChatResponse(
                success=False,
                message="Please provide a valid query.",
                agents_used=[],
                confidence=0.0,
                sources=[],
                evidence=[],
                context_used=False,
                metadata={"execution_time_seconds": 0.0}
            )

        # 1. Resolve Context
        initial_state: OrchestratorState = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "query": query_str,
            "resolved_query": query_str,
            "context_used": False,
            "needs_clarification": False,
            "clarification_message": "",
            "intent": "",
            "selected_agents": [],
            "agent_results": {},
            "final_answer": "",
            "confidence": 0.0,
            "sources": [],
            "evidence": [],
            "errors": [],
            "start_time": start_time
        }
        state = self._resolve_context_node(initial_state)

        # 2. Route
        state = self._route_node(state)

        # 3. Execute agents concurrently
        state = await self._execute_agents_node_async(state)

        # 4. Synthesize
        state = self._synthesize_node(state)

        # 5. Update context
        state = self._update_context_node(state)

        total_time = round(time.time() - start_time, 4)
        agents_used = state.get("selected_agents", [])
        primary_agent = agents_used[0] if agents_used else "academic_agent"
        agent_results = state.get("agent_results", {})
        evidence_list = state.get("evidence", [])

        raw_data = {
            name: res.model_dump() if hasattr(res, "model_dump") else str(res)
            for name, res in agent_results.items()
        }

        return ChatResponse(
            success=len(agents_used) > 0 or state.get("needs_clarification", False),
            message=state.get("final_answer", "No response generated."),
            response=state.get("final_answer", "No response generated."),
            agents_used=agents_used,
            agent_name=primary_agent,
            confidence=state.get("confidence", 0.0),
            sources=state.get("sources", []),
            evidence=evidence_list,
            context_used=state.get("context_used", False),
            raw_data=raw_data,
            metadata={
                "intent": state.get("intent", ""),
                "resolved_query": state.get("resolved_query", query_str),
                "execution_time_seconds": total_time,
                "errors": state.get("errors", [])
            }
        )

    def get_registered_agents_info(self) -> List[AgentInfo]:
        """Returns metadata for all registered specialized agents."""
        info_list = []
        for name, agent in self.agents.items():
            info_list.append(
                AgentInfo(
                    name=agent.name,
                    description=agent.description,
                    supported_queries=agent.supported_queries,
                    dataset_status="available"
                )
            )
        return info_list
