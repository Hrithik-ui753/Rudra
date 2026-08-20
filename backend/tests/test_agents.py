import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from services.json_service import JSONDataService
from agents.academic_agent import AcademicAgent
from agents.faculty_agent import FacultyAgent
from agents.timetable_agent import TimetableAgent


def test_academic_agent():
    """Test AcademicAgent query processing."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = AcademicAgent(json_service=json_service)
    
    res = agent.process("What subjects are in 1st year?")
    assert res.agent_name == "academic_agent"
    assert res.confidence > 0.5
    assert len(res.answer) > 0


def test_faculty_agent():
    """Test FacultyAgent query processing."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = FacultyAgent(json_service=json_service)
    
    res = agent.process("Who is Dr. B.Sridhar?")
    assert res.agent_name == "faculty_agent"
    assert len(res.answer) > 0


def test_timetable_agent():
    """Test TimetableAgent query processing."""
    json_service = JSONDataService(data_dir=settings.resolved_data_dir())
    agent = TimetableAgent(json_service=json_service)
    
    res = agent.process("What class is at 10:40?")
    assert res.agent_name == "timetable_agent"
    assert len(res.answer) > 0
