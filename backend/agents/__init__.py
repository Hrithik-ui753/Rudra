"""
RUDRA Smart Campus AI System - Agent Architecture
"""
from .base_agent import BaseAgent
from .orchestrator import OrchestratorAgent
from .academic_agent import AcademicAgent
from .faculty_agent import FacultyAgent
from .timetable_agent import TimetableAgent
from .examination_agent import ExaminationAgent
from .placement_agent import PlacementAgent
from .scholarship_agent import ScholarshipAgent
from .infrastructure_agent import InfrastructureAgent
from .student_services_agent import StudentServicesAgent
from .transport_agent import TransportAgent
from .library_agent import LibraryAgent
from .clubs_agent import ClubsAgent
from .events_agent import EventsAgent

__all__ = [
    "BaseAgent",
    "OrchestratorAgent",
    "AcademicAgent",
    "FacultyAgent",
    "TimetableAgent",
    "ExaminationAgent",
    "PlacementAgent",
    "ScholarshipAgent",
    "InfrastructureAgent",
    "StudentServicesAgent",
    "TransportAgent",
    "LibraryAgent",
    "ClubsAgent",
    "EventsAgent",
]

