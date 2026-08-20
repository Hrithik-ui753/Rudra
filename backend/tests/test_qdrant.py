import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from services.qdrant_service import QdrantHybridSearchService

BACKEND_DIR = Path(__file__).resolve().parent.parent

@pytest.fixture(scope="module")
def qdrant_service_instance():
    """Initializes a QdrantHybridSearchService for unit testing with isolated storage."""
    service = QdrantHybridSearchService(
        data_dir=str(BACKEND_DIR.parent / "DATA"),
        qdrant_path=str(BACKEND_DIR / "qdrant_storage_test")
    )
    # Regression: paths must resolve inside the project, never a dev machine's absolute path
    assert Path(service.data_dir) == (BACKEND_DIR.parent / "DATA").resolve()
    assert Path(service.qdrant_path) == (BACKEND_DIR / "qdrant_storage_test").resolve()
    return service

def test_qdrant_dense_encoder(qdrant_service_instance):
    """Verify 384-dimensional normalized dense vector encoding."""
    vec = qdrant_service_instance.encoder.encode("Data Structures and Algorithms")
    assert len(vec) == 384
    sq_sum = sum(v * v for v in vec)
    assert abs(sq_sum - 1.0) < 0.01

def test_qdrant_bm25_retriever(qdrant_service_instance):
    """Verify sparse BM25 keyword scoring algorithm."""
    docs = {
        "doc1": "Data Structures and Algorithms in Java",
        "doc2": "Operating Systems and Computer Architecture"
    }
    qdrant_service_instance.bm25.fit(docs)
    s1 = qdrant_service_instance.bm25.score("Data Structures", "doc1")
    s2 = qdrant_service_instance.bm25.score("Data Structures", "doc2")
    assert s1 > s2

def test_qdrant_search_as_evidence(qdrant_service_instance):
    """Verify evidence generation from hybrid vector search."""
    ev_list = qdrant_service_instance.search_as_evidence("academic syllabus", top_k=2)
    assert isinstance(ev_list, list)


def test_qdrant_default_paths_are_project_relative():
    """
    Regression: default data/qdrant paths derive from the project location
    (previously hardcoded to a developer's d:/RUDRA.1 machine paths).
    """
    svc = QdrantHybridSearchService()
    try:
        assert Path(svc.data_dir) == (BACKEND_DIR.parent / "DATA").resolve()
        assert Path(svc.qdrant_path) == (BACKEND_DIR / "qdrant_storage").resolve()
    finally:
        svc.client.close()


def test_qdrant_service_wired_in_lifespan():
    """
    Regression: /api/qdrant/* endpoints returned 503 because qdrant_service was
    never initialized. It must be created on app startup and answer requests.
    """
    import main
    with TestClient(main.app) as client:
        assert main.qdrant_service is not None
        resp = client.post("/api/qdrant/search", json={"query": "academic syllabus", "top_k": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "matches" in data
