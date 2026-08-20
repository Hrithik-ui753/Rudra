import pytest
from pathlib import Path
from services.rag_service import RAGService

BACKEND_DIR = Path(__file__).resolve().parent.parent

@pytest.fixture(scope="module")
def rag_service_instance():
    """Initializes a fast RAGService for unit testing with isolated test directory."""
    service = RAGService(
        data_dir=str(BACKEND_DIR.parent / "DATA"),
        chroma_dir=str(BACKEND_DIR / "chroma_db_test")
    )
    # Regression: paths must resolve inside the project, never a dev machine's absolute path
    assert Path(service.data_dir) == (BACKEND_DIR.parent / "DATA").resolve()
    assert Path(service.chroma_dir) == (BACKEND_DIR / "chroma_db_test").resolve()
    return service


def test_rag_default_paths_are_project_relative():
    """Regression: default ChromaDB/data paths derive from the project location."""
    svc = RAGService()
    assert Path(svc.data_dir) == (BACKEND_DIR.parent / "DATA").resolve()
    assert Path(svc.chroma_dir) == (BACKEND_DIR / "chroma_db").resolve()

def test_rag_chunking(rag_service_instance):
    """Verify text chunking algorithm correctly breaks text with overlap."""
    sample_text = "Vasavi College of Engineering was established in 1981. It offers 6 undergraduate programs in CSE, IT, ECE, EEE, Civil, and Mechanical Engineering. The campus spans over 13 acres in Ibrahimbagh, Hyderabad."
    chunks = rag_service_instance.chunk_text(sample_text, chunk_size=80, overlap=20)
    assert len(chunks) >= 2
    assert "Vasavi" in chunks[0]

def test_rag_indexing_and_search(rag_service_instance):
    """Verify document indexing and vector similarity search against ChromaDB."""
    build_res = rag_service_instance.build_vector_index()
    assert build_res["status"] == "success"
    assert build_res["total_chunks"] > 0

    # Test vector search
    matches = rag_service_instance.search("public holidays almanac", top_k=2)
    assert len(matches) > 0
    assert "source_file" in matches[0]

    # Test search as evidence
    ev_list = rag_service_instance.search_as_evidence("academic calendar syllabus", top_k=2)
    assert len(ev_list) > 0
    assert ev_list[0].source_type == "vector_db"
    assert ev_list[0].retrieval_method == "chromadb_vector_similarity"
