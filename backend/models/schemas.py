import uuid
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Structured source provenance and retrieval evidence model."""
    id: str = Field(default_factory=lambda: f"evidence_{uuid.uuid4().hex[:6]}")
    agent: str = Field(..., description="Agent name that retrieved this evidence")
    source_type: str = Field(..., description="structured_data, document, vector_database, external_web, database")
    source_name: str = Field(..., description="Human readable name of the source data")
    source_file: Optional[str] = Field(None, description="Filename of dataset or document")
    retrieval_method: str = Field(..., description="structured_json, filtered_json, exact_lookup, semantic_search, hybrid_search, database_query, external_search")
    records_matched: int = Field(0, description="Count of matched records or chunks")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria used during retrieval")
    relevance: float = Field(1.0, ge=0.0, le=1.0, description="Relevance or confidence score of retrieved evidence")
    verified: bool = Field(True, description="Whether source evidence is verified")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional source/retrieval metadata (e.g. pages for RAG)")


class EntityMemory(BaseModel):
    """Structured memory tracking key campus entities from recent turns."""
    faculty: Optional[Dict[str, Any]] = None
    subject: Optional[Dict[str, Any]] = None
    event: Optional[Dict[str, Any]] = None
    timetable: Optional[Dict[str, Any]] = None
    roll_no: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[str] = None
    last_events: List[Dict[str, Any]] = Field(default_factory=list)
    last_subjects: List[Dict[str, Any]] = Field(default_factory=list)
    candidate_faculty: List[Dict[str, Any]] = Field(default_factory=list)


class ConversationContext(BaseModel):
    """Structured multi-turn conversation context associated with (user_id, conversation_id)."""
    user_id: str
    conversation_id: str
    recent_intent: Optional[str] = None
    last_agent: Optional[str] = None
    last_agents: List[str] = Field(default_factory=list)
    last_sources: List[str] = Field(default_factory=list)
    entities: EntityMemory = Field(default_factory=EntityMemory)
    turns_count: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())


class RAGSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query for ChromaDB vector store")
    top_k: int = Field(4, ge=1, le=20, description="Number of vector chunks to retrieve")


class RAGSearchResponse(BaseModel):
    success: bool = True
    query: str
    total_matches: int
    matches: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)


class QdrantSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language query for Qdrant hybrid semantic search")
    top_k: int = Field(4, ge=1, le=20, description="Number of reranked results to retrieve")
    file_type_filter: Optional[str] = Field(None, description="Optional metadata filter: pdf or json")
    source_file_filter: Optional[str] = Field(None, description="Optional source file metadata filter")
    dense_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight for dense cosine vector score")
    sparse_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight for sparse BM25 keyword score")


class QdrantSearchResponse(BaseModel):
    success: bool = True
    query: str
    total_matches: int
    matches: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Chat input request schema supporting both 'message' and 'query' input keys."""
    message: Optional[str] = Field(None, description="User's query string")
    query: Optional[str] = Field(None, description="Alternative key for user query string")
    session_id: Optional[str] = Field(None, description="Chat session/conversation ID")
    conversation_id: Optional[str] = Field(None, description="Alternative key for chat session ID")

    def get_text(self) -> str:
        text = self.message or self.query or ""
        return text.strip()

    def get_session_id(self) -> str:
        return (self.session_id or self.conversation_id or "default_session").strip()


class ChatResponse(BaseModel):
    """Chat API response schema formatted for both API clients and rich Frontend UI."""
    success: bool = Field(True, description="Whether request was handled successfully")
    message: str = Field(..., description="Final natural-language response")
    response: Optional[str] = Field(None, description="Alias for message for frontend compatibility")
    agents_used: List[str] = Field(..., description="List of specialized agents invoked")
    agent_name: Optional[str] = Field(None, description="Primary agent name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall answer confidence score")
    sources: List[str] = Field(default_factory=list, description="List of data sources or datasets used")
    evidence: List[Evidence] = Field(default_factory=list, description="Structured source provenance and retrieval evidence")
    context_used: bool = Field(False, description="Whether conversation context was utilized to resolve references")
    suggested_followups: List[str] = Field(default_factory=list, description="Follow-up query chips")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Optional payload data for downstream client rendering")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and routing metadata")



class RoutingDecision(BaseModel):
    """Structured response model for router decision."""
    agents: List[str] = Field(..., description="List of registered agent names selected for query execution")
    reason: str = Field("", description="Reasoning for routing decision")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in routing choice")



class HealthResponse(BaseModel):
    """Health status response schema."""
    status: str = Field("ok", json_schema_extra={"example": "ok"})
    service: str = Field("RUDRA", json_schema_extra={"example": "RUDRA"})
    agents_loaded: bool = Field(True, json_schema_extra={"example": True})
    version: Optional[str] = Field("1.0.0", json_schema_extra={"example": "1.0.0"})


class AgentInfo(BaseModel):
    """Metadata describing a registered agent."""
    name: str
    description: str
    supported_queries: List[str]
    dataset_status: str = Field("available", description="Dataset availability status")


class AgentsListResponse(BaseModel):
    """Response schema listing registered agents."""
    success: bool = True
    total: int
    agents: List[AgentInfo]


class AgentResult(BaseModel):
    """Structured result returned by individual agents."""
    agent_name: str
    success: bool = True
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    answer: str
    data: Optional[Any] = None
    evidence: List[Evidence] = Field(default_factory=list)
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized API error response schema."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# Authentication & Profile Schemas
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None
    role: Optional[str] = "student"


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    role: Optional[str] = "student"
    branch: Optional[str] = None
    department: Optional[str] = None
    roll_no: Optional[str] = None
    year: Optional[str] = None
    section: Optional[str] = None
    phone: Optional[str] = None


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str = "student"
    branch: Optional[str] = "CIVIL"
    department: Optional[str] = "CIVIL"
    roll_no: Optional[str] = None
    year: Optional[str] = "1st Year"
    section: Optional[str] = "A"
    phone: Optional[str] = None


class AuthResponse(BaseModel):
    success: bool = True
    token: str
    user: UserProfile


class HistoryRow(BaseModel):
    id: str
    session_id: str
    sender: str  # "user" or "assistant"
    message: str
    created_at: str
    agent_name: Optional[str] = None
    suggested_followups: Optional[List[str]] = None


class HistoryResponse(BaseModel):
    success: bool = True
    messages: List[HistoryRow] = Field(default_factory=list)


# Campus Events & Registration Schemas
class EventItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str = "General"
    organizer: str = "VCE"
    department: Optional[str] = "College"
    date: str
    start_time: str = "09:00"
    end_time: str = "17:00"
    location: str = "Campus Auditorium / Online"
    capacity: Optional[int] = None
    registered_count: Optional[int] = 0
    registration_required: bool = True
    registration_open: bool = True
    registration_url: Optional[str] = None
    registration_deadline: Optional[str] = None
    eligibility: Optional[str] = "All Students"
    contact: Optional[str] = None
    status: str = "Upcoming"
    online: bool = False
    meeting_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    speaker: Optional[str] = None
    image: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = "institutional"  # "institutional", "unstop", "google_search"
    is_registered: Optional[bool] = False
    calendar_added: Optional[bool] = False


class EventListResponse(BaseModel):
    success: bool = True
    total: int
    events: List[EventItem]


class EventDetailResponse(BaseModel):
    success: bool = True
    event: EventItem
    user_registered: bool = False
    calendar_added: bool = False


class RegistrationStatusResponse(BaseModel):
    success: bool = True
    event_id: str
    is_registered: bool
    registration_id: Optional[str] = None
    registered_at: Optional[str] = None
    calendar_added: bool = False


class RegisterEventResponse(BaseModel):
    success: bool
    message: str
    event_id: str
    registration_id: Optional[str] = None


class CalendarActionRequest(BaseModel):
    access_token: Optional[str] = Field(None, description="Delegated Microsoft Graph access token")


class CalendarActionResponse(BaseModel):
    success: bool
    message: str
    calendar_event_id: Optional[str] = None


class MyEventsResponse(BaseModel):
    success: bool = True
    registered: List[EventItem] = Field(default_factory=list)
    upcoming: List[EventItem] = Field(default_factory=list)
    past: List[EventItem] = Field(default_factory=list)


# Notifications & Reminders Schemas
class NotificationItem(BaseModel):
    id: str
    user_id: str
    event_id: Optional[str] = None
    type: str  # 'event_reminder', 'registration_deadline', 'event_starting'
    title: str
    message: str
    scheduled_for: str
    sent_at: str
    read_at: Optional[str] = None
    created_at: str
    event_title: Optional[str] = None


class NotificationListResponse(BaseModel):
    success: bool = True
    total: int
    unread_count: int
    notifications: List[NotificationItem]


class NextEventResponse(BaseModel):
    success: bool = True
    event: Optional[EventItem] = None
    message: Optional[str] = None



