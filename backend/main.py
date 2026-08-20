import sys
from pathlib import Path
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent

# Ensure backend directory is on sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, HTTPException, Request, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
import asyncio
from models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    AgentsListResponse,
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserProfile,
    HistoryResponse,
    EventItem,
    EventListResponse,
    EventDetailResponse,
    RegistrationStatusResponse,
    RegisterEventResponse,
    CalendarActionRequest,
    CalendarActionResponse,
    MyEventsResponse,
    NotificationItem,
    NotificationListResponse,
    NextEventResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    QdrantSearchRequest,
    QdrantSearchResponse
)
from services.json_service import JSONDataService
from services.llm_service import LLMService
from services.auth_service import AuthService
from services.events_service import EventsService
from services.microsoft_calendar import MicrosoftCalendarService
from services.notification_service import NotificationService
from services.rag_service import RAGService
from services.qdrant_service import QdrantHybridSearchService


def get_authenticated_user_id(authorization: Optional[str]) -> str:
    """Resolve the authenticated user id or raise 401 when credentials are invalid/missing."""
    user_id = auth_service.resolve_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required or session token is invalid/expired."
        )
    return user_id
from agents.orchestrator import OrchestratorAgent
from utils.logger import logger

# Global Service Instances
json_service: JSONDataService = None
llm_service: LLMService = None
auth_service: AuthService = None
events_service: EventsService = None
calendar_service: MicrosoftCalendarService = None
notification_service: NotificationService = None
rag_service: RAGService = None
qdrant_service: QdrantHybridSearchService = None
orchestrator: OrchestratorAgent = None
_reminder_bg_task: Optional[asyncio.Task] = None


async def _background_reminder_loop():
    """Lightweight background loop to generate event reminders every 60 seconds."""
    while True:
        try:
            if events_service and notification_service:
                cnt = notification_service.generate_event_reminders(events_service)
                if cnt > 0:
                    logger.info(f"[BackgroundScheduler] Generated {cnt} event reminders.")
        except Exception as e:
            logger.error(f"[BackgroundScheduler] Error in reminder loop: {e}")
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global json_service, llm_service, auth_service, events_service, calendar_service, notification_service, rag_service, qdrant_service, orchestrator, _reminder_bg_task
    logger.info("Initializing RUDRA Smart Campus Backend Application...")
    
    data_dir = settings.resolved_data_dir()
    json_service = JSONDataService(data_dir=data_dir)
    llm_service = LLMService()
    auth_service = AuthService()
    events_service = EventsService(json_service=json_service)
    calendar_service = MicrosoftCalendarService()
    notification_service = NotificationService()
    rag_service = RAGService(data_dir=data_dir)
    try:
        qdrant_service = QdrantHybridSearchService(
            data_dir=data_dir,
            qdrant_path=str(BASE_DIR / "qdrant_storage")
        )
    except Exception as e:
        logger.warning(f"Qdrant service failed to initialize, /api/qdrant/* endpoints will be unavailable: {e}")
    orchestrator = OrchestratorAgent(
        json_service=json_service,
        llm_service=llm_service,
        rag_service=rag_service
    )

    # Initial reminder generation
    notification_service.generate_event_reminders(events_service)

    # Start background scheduler loop
    _reminder_bg_task = asyncio.create_task(_background_reminder_loop())
    
    logger.info("RUDRA Backend initialized with Authentication, Events, Calendar & Notification Reminders.")
    yield
    if _reminder_bg_task:
        _reminder_bg_task.cancel()
    logger.info("Shutting down RUDRA Backend...")




app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend for RUDRA Multi-Agent Smart Campus AI System with Authentication",
    lifespan=lifespan
)

# CORS Middleware Setup
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            detail=str(exc.detail)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Internal Server Error",
            detail="An unexpected error occurred while processing your request."
        ).model_dump()
    )


# Helper functions for follow-up chips
def generate_followup_suggestions(agent_names: list[str], raw_data: Optional[dict] = None) -> list[str]:
    """Generate intelligent follow-up prompt chips based on invoked agents and retrieved context."""
    suggestions = []
    if "faculty_agent" in agent_names:
        suggestions.extend(["When is his next class?", "What subjects does he teach?", "Where is his office?"])
    if "events_agent" in agent_names:
        suggestions.extend(["Register me for it", "Tell me more about it", "Add it to my calendar"])
    if "academic_agent" in agent_names:
        suggestions.extend(["How many credits does the first subject have?", "Who teaches Data Structures?", "What are the subjects in 3rd semester?"])
    if "timetable_agent" in agent_names:
        suggestions.extend(["What class is at 10:40?", "Where is his next class?"])
    if "placement_agent" in agent_names:
        suggestions.extend(["What is Flipkart package?", "Show placement statistics for ServiceNow"])
    if "scholarship_agent" in agent_names:
        suggestions.extend(["Tell me about TS ePASS scholarship", "What are the fee payment deadlines?"])
    if "transport_agent" in agent_names:
        suggestions.extend(["Which bus route goes to ECIL?", "What is the transport fee?"])
    if "library_agent" in agent_names:
        suggestions.extend(["Is Theory of Computation book available?", "What is the library fine policy?"])
    if "clubs_agent" in agent_names:
        suggestions.extend(["Tell me about Rangmanch club", "How do I register for student clubs?"])

    if not suggestions:
        suggestions = ["What are the subjects in 1st year?", "Who is Dr. B.Sridhar?", "When are the Mid exams?"]
    return list(dict.fromkeys(suggestions))[:3]


# API Endpoints
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint returning system status."""
    is_loaded = bool(orchestrator and hasattr(orchestrator, "agents") and len(orchestrator.agents) > 0)
    return HealthResponse(
        status="ok",
        service="RUDRA",
        agents_loaded=is_loaded,
        version=settings.VERSION
    )


@app.get("/api/agents", response_model=AgentsListResponse, tags=["Agents"])
async def get_agents():
    """Returns list of all available specialized agents and their descriptions."""
    if not orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator service is initializing."
        )
    agents_info = orchestrator.get_registered_agents_info()
    return AgentsListResponse(
        success=True,
        total=len(agents_info),
        agents=agents_info
    )


# Authentication & Profile Endpoints
@app.post("/api/auth/login", response_model=AuthResponse, tags=["Authentication"])
async def login(req: LoginRequest):
    """Authenticate user and return access token and user profile."""
    user_id = f"user_{req.email.split('@')[0]}"
    profile = auth_service.get_or_create_profile(user_id, default_name=req.email.split('@')[0].capitalize())
    if req.role:
        profile = auth_service.update_profile(user_id, {"role": req.role})
    token = f"user_{user_id}"
    return AuthResponse(success=True, token=token, user=profile)


@app.post("/api/auth/register", response_model=AuthResponse, tags=["Authentication"])
async def register(req: RegisterRequest):
    """Register user and create user profile."""
    user_id = f"user_{req.email.split('@')[0]}"
    profile = auth_service.get_or_create_profile(user_id, default_name=req.name)
    profile = auth_service.update_profile(user_id, req.model_dump(exclude_unset=True))
    token = f"user_{user_id}"
    return AuthResponse(success=True, token=token, user=profile)


@app.get("/api/profile", response_model=UserProfile, tags=["Profile"])
async def get_profile(authorization: Optional[str] = Header(None)):
    """Retrieve current user profile."""
    user_id = auth_service.extract_user_id_from_header(authorization)
    return auth_service.get_or_create_profile(user_id)


@app.put("/api/profile", response_model=UserProfile, tags=["Profile"])
async def update_profile(patch: Dict[str, Any], authorization: Optional[str] = Header(None)):
    """Update current user profile."""
    user_id = get_authenticated_user_id(authorization)
    return auth_service.update_profile(user_id, patch)


@app.get("/api/history", response_model=HistoryResponse, tags=["History"])
async def get_chat_history(authorization: Optional[str] = Header(None)):
    """Retrieve stored chat history rows for current user."""
    user_id = get_authenticated_user_id(authorization)
    rows = auth_service.get_user_history(user_id)
    return HistoryResponse(success=True, messages=rows)


# Chat Communication Endpoint
@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    Main natural-language chat interface. Resolves context and references through OrchestratorAgent,
    invokes specialized agents, saves conversation history, and returns full response.
    """
    query = request.get_text()
    if not query:
        return ChatResponse(
            success=False,
            message="Query message cannot be empty.",
            response="Query message cannot be empty.",
            agents_used=[],
            confidence=0.0,
            sources=[],
            evidence=[],
            context_used=False,
            metadata={"error": "Empty Query"}
        )

    user_id = get_authenticated_user_id(authorization)
    session_id = request.get_session_id()

    logger.info(f"Incoming Query from [{user_id}] (session '{session_id}'): '{query}'")

    # 1. Record user query message in history
    auth_service.add_history_message(user_id, session_id, sender="user", message=query)

    try:
        # 2. Process query asynchronously via OrchestratorAgent LangGraph pipeline with context resolution
        orch_res = await orchestrator.process_query_async(query, user_id=user_id, conversation_id=session_id)
        primary_agent = orch_res.agents_used[0] if orch_res.agents_used else "academic_agent"
        followups = generate_followup_suggestions(orch_res.agents_used, orch_res.raw_data)

        # 3. Record assistant response in history
        auth_service.add_history_message(
            user_id,
            session_id,
            sender="assistant",
            message=orch_res.message,
            agent_name=primary_agent,
            suggested_followups=followups
        )

        # 4. Return response payload with full schema compatibility
        return ChatResponse(
            success=orch_res.success,
            message=orch_res.message,
            response=orch_res.message,
            agents_used=orch_res.agents_used,
            agent_name=primary_agent,
            confidence=orch_res.confidence,
            sources=orch_res.sources,
            evidence=orch_res.evidence,
            context_used=orch_res.context_used,
            suggested_followups=followups,
            raw_data=orch_res.raw_data,
            metadata=orch_res.metadata
        )

    except Exception as e:
        logger.error(f"Error processing chat query: {e}", exc_info=True)
        return ChatResponse(
            success=False,
            message="I was unable to process that request right now.",
            response="I was unable to process that request right now.",
            agents_used=[],
            confidence=0.0,
            sources=[],
            metadata={"error": str(e)}
        )


# Events & Activities API Endpoints
@app.get("/api/events", response_model=EventListResponse, tags=["Events"])
async def get_events(
    category: Optional[str] = None,
    department: Optional[str] = None,
    timeframe: Optional[str] = None,
    eligibility: Optional[str] = None,
    query: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """Retrieve campus & external hackathon events with filtering."""
    if not events_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = auth_service.extract_user_id_from_header(authorization)
    events_list = events_service.get_events(
        category=category,
        department=department,
        timeframe=timeframe,
        eligibility=eligibility,
        query=query,
        user_id=user_id
    )
    return EventListResponse(success=True, total=len(events_list), events=events_list)


@app.get("/api/events/{event_id}", response_model=EventDetailResponse, tags=["Events"])
async def get_event_detail(event_id: str, authorization: Optional[str] = Header(None)):
    """Retrieve single event details by ID."""
    if not events_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = auth_service.extract_user_id_from_header(authorization)
    evt = events_service.get_event_by_id(event_id, user_id=user_id)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found.")
    
    is_reg = bool(evt.is_registered)
    is_cal = bool(evt.calendar_added)
    return EventDetailResponse(success=True, event=evt, user_registered=is_reg, calendar_added=is_cal)


@app.post("/api/events/{event_id}/register", response_model=RegisterEventResponse, tags=["Events"])
async def register_event(event_id: str, authorization: Optional[str] = Header(None)):
    """Register authenticated user for an event."""
    if not events_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = get_authenticated_user_id(authorization)
    res = events_service.register_user_for_event(user_id=user_id, event_id=event_id)
    return RegisterEventResponse(**res)


@app.get("/api/events/{event_id}/registration", response_model=RegistrationStatusResponse, tags=["Events"])
async def get_event_registration_status(event_id: str, authorization: Optional[str] = Header(None)):
    """Get current user's registration status for an event."""
    if not events_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = get_authenticated_user_id(authorization)
    reg = events_service.get_user_registration(user_id, event_id)
    cal = events_service.get_calendar_entry(user_id, event_id)
    
    is_reg = bool(reg and reg.get("status") == "registered")
    reg_id = reg.get("id") if reg else None
    reg_at = reg.get("registered_at") if reg else None

    return RegistrationStatusResponse(
        success=True,
        event_id=event_id,
        is_registered=is_reg,
        registration_id=reg_id,
        registered_at=reg_at,
        calendar_added=bool(cal)
    )


@app.delete("/api/events/{event_id}/register", tags=["Events"])
async def cancel_event_registration(event_id: str, authorization: Optional[str] = Header(None)):
    """Cancel authenticated user's event registration."""
    if not events_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = get_authenticated_user_id(authorization)
    res = events_service.cancel_registration(user_id=user_id, event_id=event_id)
    return res


@app.post("/api/events/{event_id}/calendar", response_model=CalendarActionResponse, tags=["Events & Microsoft Calendar"])
async def add_event_to_microsoft_calendar(
    event_id: str,
    req: CalendarActionRequest,
    authorization: Optional[str] = Header(None)
):
    """Add event to user's Microsoft 365 Outlook Calendar."""
    if not events_service or not calendar_service:
        raise HTTPException(status_code=503, detail="Calendar service initializing.")
    user_id = get_authenticated_user_id(authorization)
    
    # Check duplicate entry
    existing_cal = events_service.get_calendar_entry(user_id, event_id)
    if existing_cal:
        return CalendarActionResponse(
            success=True,
            message="Event is already added to your Microsoft Calendar.",
            calendar_event_id=existing_cal.get("microsoft_event_id")
        )

    evt = events_service.get_event_by_id(event_id)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found.")

    res = calendar_service.create_event(access_token=req.access_token, event=evt)
    if res.get("success") and res.get("calendar_event_id"):
        events_service.record_calendar_entry(user_id, event_id, res["calendar_event_id"])

    return CalendarActionResponse(**res)


@app.delete("/api/events/{event_id}/calendar", response_model=CalendarActionResponse, tags=["Events & Microsoft Calendar"])
async def remove_event_from_microsoft_calendar(
    event_id: str,
    req: CalendarActionRequest,
    authorization: Optional[str] = Header(None)
):
    """Remove event from user's Microsoft 365 Outlook Calendar."""
    if not events_service or not calendar_service:
        raise HTTPException(status_code=503, detail="Calendar service initializing.")
    user_id = get_authenticated_user_id(authorization)

    ms_id = events_service.delete_calendar_entry(user_id, event_id)
    if ms_id:
        res = calendar_service.delete_event(access_token=req.access_token, microsoft_event_id=ms_id)
        return CalendarActionResponse(**res)

    return CalendarActionResponse(success=True, message="Calendar event removed.")


@app.get("/api/my-events", response_model=MyEventsResponse, tags=["Events"])
async def get_my_events(authorization: Optional[str] = Header(None)):
    """Retrieve current authenticated user's registered, upcoming, and past events."""
    if not events_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = get_authenticated_user_id(authorization)
    res_dict = events_service.get_my_events(user_id)
    return MyEventsResponse(success=True, **res_dict)


@app.get("/api/my-events/next", response_model=NextEventResponse, tags=["Events"])
async def get_next_registered_event(authorization: Optional[str] = Header(None)):
    """Retrieve the current user's nearest upcoming registered event."""
    if not events_service or not notification_service:
        raise HTTPException(status_code=503, detail="Events service initializing.")
    user_id = get_authenticated_user_id(authorization)
    next_evt = notification_service.get_next_registered_event(user_id, events_service)
    if not next_evt:
        return NextEventResponse(success=True, event=None, message="No upcoming registered events found.")
    return NextEventResponse(success=True, event=next_evt, message=f"Next event is '{next_evt.title}'.")


# Notification & Reminders API Endpoints
@app.get("/api/notifications", response_model=NotificationListResponse, tags=["Notifications"])
async def get_notifications(unread_only: bool = False, authorization: Optional[str] = Header(None)):
    """Retrieve notifications for the authenticated user."""
    if not notification_service or not events_service:
        raise HTTPException(status_code=503, detail="Notification service initializing.")
    user_id = get_authenticated_user_id(authorization)
    
    # Refresh reminders
    notification_service.generate_event_reminders(events_service)
    
    notifs = notification_service.get_user_notifications(user_id, unread_only=unread_only, events_service=events_service)
    unread_cnt = len([n for n in notification_service.get_user_notifications(user_id) if not n.read_at])
    
    return NotificationListResponse(
        success=True,
        total=len(notifs),
        unread_count=unread_cnt,
        notifications=notifs
    )


@app.patch("/api/notifications/{notification_id}/read", tags=["Notifications"])
async def mark_notification_read(notification_id: str, authorization: Optional[str] = Header(None)):
    """Mark a specific notification as read."""
    if not notification_service:
        raise HTTPException(status_code=503, detail="Notification service initializing.")
    user_id = get_authenticated_user_id(authorization)
    ok = notification_service.mark_as_read(user_id, notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found or unauthorized.")
    return {"success": True, "message": "Notification marked as read."}


@app.patch("/api/notifications/read-all", tags=["Notifications"])
async def mark_all_notifications_read(authorization: Optional[str] = Header(None)):
    """Mark all notifications for current user as read."""
    if not notification_service:
        raise HTTPException(status_code=503, detail="Notification service initializing.")
    user_id = get_authenticated_user_id(authorization)
    cnt = notification_service.mark_all_as_read(user_id)
    return {"success": True, "message": f"Marked {cnt} notifications as read."}


@app.post("/api/rag/search", response_model=RAGSearchResponse, tags=["RAG & ChromaDB"])
async def rag_vector_search(payload: RAGSearchRequest):
    """
    Search ChromaDB vector database using natural language embeddings.
    Returns matched chunks and structured Evidence objects.
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service initializing.")
    matches = rag_service.search(payload.query, top_k=payload.top_k)
    evidence = rag_service.search_as_evidence(payload.query, top_k=payload.top_k)
    return RAGSearchResponse(
        success=True,
        query=payload.query,
        total_matches=len(matches),
        matches=matches,
        evidence=evidence
    )


@app.post("/api/rag/ingest", tags=["RAG & ChromaDB"])
async def rag_reindex_documents():
    """
    Re-index all campus JSON and PDF documents into ChromaDB vector store.
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service initializing.")
    res = rag_service.build_vector_index()
    return {"success": True, "details": res}


@app.post("/api/qdrant/search", response_model=QdrantSearchResponse, tags=["Qdrant Hybrid Search"])
async def qdrant_hybrid_search(payload: QdrantSearchRequest):
    """
    Perform Qdrant-based Hybrid Semantic Search:
    - Dense Cosine Vector Similarity (384-dim)
    - Sparse BM25 Keyword Search
    - Metadata Filtering (file_type, source_file)
    - Reciprocal Rank Fusion (RRF) Reranking Engine
    """
    if not qdrant_service:
        raise HTTPException(status_code=503, detail="Qdrant service initializing.")
    matches = qdrant_service.search_hybrid(
        query=payload.query,
        top_k=payload.top_k,
        file_type_filter=payload.file_type_filter,
        source_file_filter=payload.source_file_filter,
        dense_weight=payload.dense_weight,
        sparse_weight=payload.sparse_weight
    )
    evidence = qdrant_service.search_as_evidence(payload.query, top_k=payload.top_k)
    return QdrantSearchResponse(
        success=True,
        query=payload.query,
        total_matches=len(matches),
        matches=matches,
        evidence=evidence
    )


@app.post("/api/qdrant/ingest", tags=["Qdrant Hybrid Search"])
async def qdrant_ingest_documents():
    """
    Ingest and index all campus PDF and JSON documents into Qdrant vector database.
    """
    if not qdrant_service:
        raise HTTPException(status_code=503, detail="Qdrant service initializing.")
    res = qdrant_service.ingest_documents()
    return {"success": True, "details": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )


