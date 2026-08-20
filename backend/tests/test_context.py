import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from services.json_service import JSONDataService
from services.context_service import ConversationContextService
from agents.orchestrator import OrchestratorAgent
from config import settings


def test_context_service_basic_resolution():
    """1. Test ConversationContextService reference resolution and context isolation."""
    svc = ConversationContextService()
    
    # Update context with faculty entity
    svc.update_context(
        user_id="user_a",
        conversation_id="session_1",
        query="Who is Dr. B.Sridhar?",
        agents_used=["faculty_agent"],
        agent_results={
            "faculty_agent": type("Res", (), {
                "success": True,
                "data": {"faculty_profile": {"Name": "Dr. B.Sridhar", "Faculty ID": "FAC-2325"}}
            })()
        },
        final_answer="Dr. B.Sridhar is Professor in Civil Dept."
    )
    
    # Turn 2: Pronoun reference "When is his next class?"
    resolved_q, context_used, needs_clar, clar_msg = svc.resolve_context(
        user_id="user_a",
        conversation_id="session_1",
        query="When is his next class?"
    )
    assert context_used is True
    assert "Dr. B.Sridhar" in resolved_q
    assert needs_clar is False

    # User B should NOT share User A's context (User Isolation Test)
    resolved_q_b, context_used_b, _, _ = svc.resolve_context(
        user_id="user_b",
        conversation_id="session_1",
        query="When is his next class?"
    )
    assert context_used_b is False
    assert "Dr. B.Sridhar" not in resolved_q_b


def test_ambiguous_faculty_reference():
    """2. Ambiguous reference handling returns clarification instead of guessing."""
    svc = ConversationContextService()
    ctx = svc.get_context("user_a", "session_ambig")
    ctx.entities.candidate_faculty = [
        {"name": "Dr. Kumar"},
        {"name": "Dr. Sridhar"}
    ]
    ctx.entities.faculty = None
    
    resolved_q, context_used, needs_clar, clar_msg = svc.resolve_context(
        user_id="user_a",
        conversation_id="session_ambig",
        query="When is his class?"
    )
    assert needs_clar is True
    assert "Which faculty member do you mean?" in clar_msg
    assert "Dr. Kumar" in clar_msg


def test_positional_subject_and_credits_followup():
    """3. Academic follow-up: 'What subjects are in 3rd semester IT?' -> 'How many credits does the first subject have?'"""
    svc = ConversationContextService()
    svc.update_context(
        user_id="user_a",
        conversation_id="session_acad",
        query="What subjects are in 3rd semester IT?",
        agents_used=["academic_agent"],
        agent_results={
            "academic_agent": type("Res", (), {
                "success": True,
                "data": {
                    "sample": {"Subjects": "Strength of Materials-I", "Credits": "3", "Branch": "CIVIL", "Semester": "III"}
                }
            })()
        },
        final_answer="Subjects include Strength of Materials-I"
    )

    resolved_q, context_used, _, _ = svc.resolve_context(
        user_id="user_a",
        conversation_id="session_acad",
        query="How many credits does the first subject have?"
    )
    assert context_used is True
    assert "Strength of Materials-I" in resolved_q


def test_event_followup_and_registration():
    """4. Event follow-up: 'What workshops are happening?' -> 'Register me for it'."""
    svc = ConversationContextService()
    svc.update_context(
        user_id="user_a",
        conversation_id="session_evt",
        query="What workshops are happening?",
        agents_used=["events_agent"],
        agent_results={
            "events_agent": type("Res", (), {
                "success": True,
                "data": {
                    "events": [{"id": "EVT-101", "title": "AI Workshop", "date": "2026-09-15"}]
                }
            })()
        },
        final_answer="Found AI Workshop"
    )

    resolved_q, context_used, _, _ = svc.resolve_context(
        user_id="user_a",
        conversation_id="session_evt",
        query="Register me for it"
    )
    assert context_used is True
    assert "AI Workshop" in resolved_q
    assert "EVT-101" in resolved_q


def test_temporal_reference_resolution():
    """5. Temporal reference resolution ('today', 'tomorrow')."""
    svc = ConversationContextService()
    resolved_q, context_used, _, _ = svc.resolve_context(
        user_id="user_a",
        conversation_id="session_temp",
        query="What classes are scheduled tomorrow?"
    )
    assert context_used is True
    assert "tomorrow (" in resolved_q


def test_orchestrator_multi_turn_followup():
    """6. End-to-end multi-turn orchestrator follow-up flow."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    orchestrator = OrchestratorAgent(json_service=json_service)

    conv_id = "test_conv_flow_101"

    # Turn 1
    resp1 = orchestrator.process_query("Who is Dr. B.Sridhar?", user_id="user_test", conversation_id=conv_id)
    assert resp1.success is True

    # Turn 2
    resp2 = orchestrator.process_query("When is his next class?", user_id="user_test", conversation_id=conv_id)
    assert resp2.success is True
    assert resp2.context_used is True
