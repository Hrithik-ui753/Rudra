import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from services.json_service import JSONDataService
from agents.orchestrator import OrchestratorAgent


def test_orchestrator_routing_and_execution():
    """Test Orchestrator routing query to specialized agent."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    orchestrator = OrchestratorAgent(json_service=json_service)
    
    response = orchestrator.process_query("What subjects are in 3rd semester?")
    assert response.success is True
    assert "academic_agent" in response.agents_used
    assert len(response.message) > 0


def test_orchestrator_multi_agent():
    """Test Orchestrator multi-agent query routing."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    orchestrator = OrchestratorAgent(json_service=json_service)
    
    response = orchestrator.process_query("Where is Dr. B.Sridhar teaching at 10:40?")
    assert response.success is True
    assert len(response.agents_used) >= 1
