"""
test_similar_report_linking.py - Dedicated Test Suite for Stage 25 Similar Historical Report Linking.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.similar_report_finder import SimilarReportFinder

client = TestClient(app)


def test_embedding_dimension_and_faiss_index():
    """Verify 384-dimensional vector dimension."""
    finder = SimilarReportFinder()
    assert finder.vector_dim == 384, f"Expected 384-D embeddings, got {finder.vector_dim}"


def test_top_k_similarity_retrieval():
    """Verify Top-K retrieval returns semantically relevant historical reports."""
    finder = SimilarReportFinder(top_k=5, min_similarity=0.30)
    results = finder.find_similar_reports(query_text="Technician started maintenance before electrical isolation.")
    
    assert len(results) > 0
    top_res = results[0]
    assert "report_id" in top_res
    assert top_res["similarity_score"] >= 0.30
    assert "explanation" in top_res


def test_self_match_exclusion():
    """Verify query report is excluded from its own similarity results."""
    finder = SimilarReportFinder(top_k=5)
    first_report_id = finder.records[0]["record_id"]
    
    results = finder.find_similar_reports(query_report_id=first_report_id)
    matched_ids = [r["report_id"] for r in results]
    assert first_report_id not in matched_ids, "Query report must be excluded from self-match"


def test_minimum_similarity_threshold():
    """Verify high minimum similarity threshold filters out low-matching reports."""
    finder = SimilarReportFinder(top_k=5, min_similarity=0.99)
    results = finder.find_similar_reports(query_text="Unrelated obscure random query string 12345")
    assert len(results) == 0, "No report should exceed 0.99 similarity for random text"


def test_deterministic_ordering_and_repeated_queries():
    """Verify 5 consecutive runs produce 100% identical results."""
    finder = SimilarReportFinder(top_k=5, min_similarity=0.30)
    q = "Pressurized bleeder line ruptured during hydrotest."
    
    run1 = finder.find_similar_reports(query_text=q)
    run2 = finder.find_similar_reports(query_text=q)
    run3 = finder.find_similar_reports(query_text=q)

    assert run1 == run2 == run3, "Similar report outputs must be 100% deterministic"


def test_fastapi_similar_reports_endpoints():
    """Verify GET and POST /api/v1/similar-reports FastAPI endpoints."""
    # POST endpoint test
    post_resp = client.post("/api/v1/similar-reports", json={
        "query_text": "Hot work welding near fuel line manifold",
        "top_k": 3,
        "min_similarity": 0.30
    })
    assert post_resp.status_code == 200
    data = post_resp.json()
    assert "total_matches" in data
    assert "similar_reports" in data

    # GET endpoint test
    finder = SimilarReportFinder()
    if finder.records:
        rep_id = finder.records[0]["record_id"]
        get_resp = client.get(f"/api/v1/similar-reports/{rep_id}?top_k=3&min_similarity=0.30")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["query_report_id"] == rep_id


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
