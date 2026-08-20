import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from services.json_service import JSONDataService


def test_json_service_discovery():
    """Verify JSONDataService discovers and preloads JSON datasets."""
    data_dir = settings.resolved_data_dir()
    json_service = JSONDataService(data_dir=data_dir)
    
    # Check that datasets were loaded
    assert json_service.is_dataset_available("faculty_timetable") or len(json_service._cache) > 0


def test_json_service_search():
    """Verify in-memory dataset search functionality."""
    data_dir = settings.resolved_data_dir()
    json_service = JSONDataService(data_dir=data_dir)
    
    results = json_service.search_in_dataset("faculty_timetable", "Sridhar")
    assert isinstance(results, list)
