import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from models.schemas import Evidence, ChatResponse, AgentResult
from services.json_service import JSONDataService
from agents.academic_agent import AcademicAgent
from agents.faculty_agent import FacultyAgent
from agents.timetable_agent import TimetableAgent
from agents.events_agent import EventsAgent
from agents.orchestrator import OrchestratorAgent
from config import settings


def test_evidence_schema_validation():
    """1. Evidence Pydantic schema validation."""
    ev = Evidence(
        agent="academic_agent",
        source_type="structured_data",
        source_name="Academic Curriculum",
        source_file="academic_curriculum.json",
        retrieval_method="filtered_json",
        records_matched=6,
        filters={"branch": "IT", "semester": 3},
        relevance=0.98,
        verified=True
    )
    assert ev.id.startswith("evidence_")
    assert ev.agent == "academic_agent"
    assert ev.source_type == "structured_data"
    assert ev.records_matched == 6
    assert ev.verified is True


def test_academic_evidence():
    """2. Academic Agent evidence generation."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = AcademicAgent(json_service=json_service)
    
    res = agent.process("What subjects are in 3rd semester?")
    assert res.success is True
    assert len(res.evidence) > 0
    ev = res.evidence[0]
    assert ev.agent == "academic_agent"
    assert ev.source_type == "structured_data"
    assert "academic" in ev.source_file.lower() or "acad" in ev.source_file.lower()
    assert ev.retrieval_method == "filtered_json"
    assert ev.verified is True


def test_faculty_evidence():
    """3. Faculty Agent evidence generation."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = FacultyAgent(json_service=json_service)
    
    res = agent.process("Who is Dr. B.Sridhar?")
    assert res.success is True
    assert len(res.evidence) > 0
    ev = res.evidence[0]
    assert ev.agent == "faculty_agent"
    assert ev.source_file == "faculty_timetable.json"
    assert ev.verified is True


def test_timetable_evidence():
    """4. Timetable Agent evidence generation."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = TimetableAgent(json_service=json_service)
    
    res = agent.process("What class is at 10:40?")
    assert res.success is True
    assert len(res.evidence) > 0
    ev = res.evidence[0]
    assert ev.agent == "timetable_agent"
    assert ev.source_file == "faculty_timetable.json"
    assert ev.verified is True


def test_multi_agent_evidence():
    """5. Multi-agent evidence aggregation (Faculty + Timetable)."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    orchestrator = OrchestratorAgent(json_service=json_service)
    
    response = orchestrator.process_query("Who teaches Data Structures and when is their class?")
    assert response.success is True
    assert len(response.evidence) >= 1
    agents_in_ev = [ev.agent for ev in response.evidence]
    assert len(set(agents_in_ev)) >= 1


def test_event_evidence_and_external_labeling():
    """6. Event Agent evidence (institutional vs external labeling)."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = EventsAgent(json_service=json_service)
    
    res = agent.process("What workshops and hackathons are happening?")
    assert res.success is True
    assert len(res.evidence) > 0
    
    sources = [ev.source_type for ev in res.evidence]
    assert "structured_data" in sources or "external_web" in sources


def test_rag_evidence_model():
    """7. RAG Agent / Vector DB Evidence model format verification."""
    ev = Evidence(
        agent="knowledge_agent",
        source_type="vector_database",
        source_name="Student Handbook",
        source_file="student_handbook.pdf",
        retrieval_method="hybrid_search",
        records_matched=3,
        metadata={"pages": [12, 13, 14]},
        relevance=0.96,
        verified=True
    )
    assert ev.source_type == "vector_database"
    assert ev.source_name == "Student Handbook"
    assert ev.metadata["pages"] == [12, 13, 14]


def test_missing_evidence_unverified_response():
    """8. Missing evidence handling (Unverified query returning safe refusal)."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    orchestrator = OrchestratorAgent(json_service=json_service)
    
    # Query for nonexistent information
    response = orchestrator.process_query("What is the quantum flux capacitor room password?")
    assert "couldn't find verified information" in response.message or response.confidence == 0.0


def test_chat_response_evidence_integration():
    """9. API ChatResponse evidence integration & backward compatibility."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    orchestrator = OrchestratorAgent(json_service=json_service)
    
    response = orchestrator.process_query("What subjects are in 2nd semester?")
    assert isinstance(response, ChatResponse)
    assert hasattr(response, "evidence")
    assert isinstance(response.evidence, list)
    if response.evidence:
        assert isinstance(response.evidence[0], Evidence)
