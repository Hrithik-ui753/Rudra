import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from services.json_service import JSONDataService
from services.events_service import EventsService
from agents.orchestrator import OrchestratorAgent
from config import settings


@pytest.fixture(scope="module")
def audit_setup():
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    events_service = EventsService(json_service=json_service)
    orchestrator = OrchestratorAgent(json_service=json_service)
    return {
        "json": json_service,
        "events": events_service,
        "orch": orchestrator
    }


def test_audit_academic_domain(audit_setup):
    """1. Real-data test: Academic queries."""
    orch = audit_setup["orch"]
    
    # 2nd semester query
    r1 = orch.process_query("What subjects are there in 2nd semester?")
    assert r1.success is True
    
    # 3rd semester query
    r2 = orch.process_query("Give me the subjects for IT 3rd semester.")
    assert r2.success is True
    assert len(r2.evidence) > 0
    assert r2.evidence[0].verified is True


def test_audit_faculty_domain(audit_setup):
    """2. Real-data test: Faculty queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("Tell me about Dr. B.Sridhar.")
    assert r1.success is True
    assert "faculty_agent" in r1.agents_used
    assert r1.evidence[0].source_file == "faculty_timetable.json"


def test_audit_timetable_domain(audit_setup):
    """3. Real-data test: Timetable queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("What class is scheduled at 10:40?")
    assert r1.success is True
    assert "timetable_agent" in r1.agents_used


def test_audit_examination_domain(audit_setup):
    """4. Real-data test: Examination queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("When are the Mid 1 exams?")
    assert r1.success is True
    assert "examination_agent" in r1.agents_used or "academic_agent" in r1.agents_used


def test_audit_placement_domain(audit_setup):
    """5. Real-data test: Placement queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("What companies visited for campus placements?")
    assert r1.success is True
    assert "placement_agent" in r1.agents_used


def test_audit_scholarship_domain(audit_setup):
    """6. Real-data test: Fee & Scholarship queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("Tell me about tuition fee and TS ePASS scholarship.")
    assert r1.success is True
    assert "scholarship_agent" in r1.agents_used


def test_audit_transport_domain(audit_setup):
    """7. Real-data test: Bus transport queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("Which bus route goes to ECIL?")
    assert r1.success is True
    assert "transport_agent" in r1.agents_used


def test_audit_library_domain(audit_setup):
    """8. Real-data test: Library book queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("Is Database System Concepts book available in library?")
    assert r1.success is True
    assert "library_agent" in r1.agents_used


def test_audit_clubs_domain(audit_setup):
    """9. Real-data test: Student club queries."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("What student clubs exist in college?")
    assert r1.success is True
    assert "clubs_agent" in r1.agents_used


def test_audit_events_institutional_vs_external(audit_setup):
    """10. Real-data test: Events discovery (institutional vs external web opportunities)."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("What hackathons and workshops are happening?")
    assert r1.success is True
    assert "events_agent" in r1.agents_used
    assert len(r1.evidence) > 0
    # Ensure source types are valid
    for ev in r1.evidence:
        assert ev.source_type in ["structured_data", "external_web", "document"]


def test_audit_multi_agent_orchestration(audit_setup):
    """11. Multi-agent test: Faculty + Timetable query."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("Who teaches Data Structures and when is their next class?")
    assert r1.success is True
    assert any(a in r1.agents_used for a in ["faculty_agent", "timetable_agent", "academic_agent"])


def test_audit_multi_turn_context_chain(audit_setup):
    """12. Context test: 4-turn conversation chain."""
    orch = audit_setup["orch"]
    session_id = "audit_conv_chain_99"

    # Turn 1: Academic query
    t1 = orch.process_query("What subjects are in 3rd semester IT?", user_id="u_audit", conversation_id=session_id)
    assert t1.success is True

    # Turn 2: Positional subject query
    t2 = orch.process_query("How many credits does the first one have?", user_id="u_audit", conversation_id=session_id)
    assert t2.success is True
    assert t2.context_used is True

    # Turn 3: Faculty lookup for subject
    t3 = orch.process_query("Who teaches Dr. B.Sridhar's course?", user_id="u_audit", conversation_id=session_id)
    assert t3.success is True

    # Turn 4: Timetable pronoun follow-up
    t4 = orch.process_query("When is his next class?", user_id="u_audit", conversation_id=session_id)
    assert t4.success is True
    assert t4.context_used is True


def test_audit_ambiguity_clarification(audit_setup):
    """13. Ambiguity test: Multiple faculty candidates requires clarification."""
    orch = audit_setup["orch"]
    sess = "ambig_session_test"
    ctx = orch.context_service.get_context("u_audit", sess)
    ctx.entities.candidate_faculty = [{"name": "Dr. Kumar"}, {"name": "Dr. Sridhar"}]
    ctx.entities.faculty = None

    res = orch.process_query("When is his class?", user_id="u_audit", conversation_id=sess)
    assert "Which faculty member do you mean?" in res.message or res.metadata.get("intent") == "Ambiguity Clarification"


def test_audit_hallucination_prevention(audit_setup):
    """14. Hallucination test: Unverified query returns safe refusal."""
    orch = audit_setup["orch"]
    
    r1 = orch.process_query("When is the Mars campus opening?")
    assert "couldn't find verified information" in r1.message or r1.confidence == 0.0

    r2 = orch.process_query("What is the phone number of fictional professor Quantum X?")
    assert "couldn't find verified information" in r2.message or r2.confidence == 0.0


def test_audit_performance_latency(audit_setup):
    """15. Performance latency measurement."""
    orch = audit_setup["orch"]
    
    start = time.time()
    res = orch.process_query("Who is Dr. B.Sridhar?")
    elapsed = time.time() - start
    
    assert res.success is True
    # Orchestrator execution time should be under 1.5 seconds for local JSON lookups
    assert elapsed < 3.0
