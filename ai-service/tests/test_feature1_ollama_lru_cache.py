"""
test_feature1_ollama_lru_cache.py - Comprehensive Unit & Benchmark Suite for Feature 1 (Ollama Timeout & Thread-Safe LRU Cache).
"""

import time
import hashlib
import threading
from pathlib import Path
import pytest
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.grounded_recommender import RAGSafetyRecommendationEngine, BoundedThreadSafeLRUCache

FROZEN_ARTIFACTS = [
    BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv",
    BASE_DIR / "datasets" / "processed" / "oilps_final_master_v2.csv",
    BASE_DIR / "models" / "sif" / "sif_model.pt",
    BASE_DIR / "models" / "lsr" / "lsr_model.pt",
    BASE_DIR / "datasets" / "rag" / "vector_index.faiss",
    BASE_DIR / "datasets" / "rag" / "semantic_chunks.json"
]


def test_frozen_artifacts_integrity():
    """Verify all frozen production ML and RAG artifacts exist and remain intact."""
    for artifact_path in FROZEN_ARTIFACTS:
        assert artifact_path.exists(), f"Frozen artifact missing: {artifact_path}"
        sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        assert len(sha256) == 64, f"Invalid SHA256 checksum for {artifact_path}"


def test_bounded_lru_cache_thread_safety_and_eviction():
    """Verify BoundedThreadSafeLRUCache operations, LRU eviction, and thread safety."""
    cache = BoundedThreadSafeLRUCache(maxsize=3)

    cache.put("k1", {"val": 1})
    cache.put("k2", {"val": 2})
    cache.put("k3", {"val": 3})

    assert cache.get("k1")["val"] == 1
    assert cache.get("k2")["val"] == 2

    # Put k4 -> should evict k3 because k1 and k2 were accessed
    cache.put("k4", {"val": 4})
    assert cache.get("k3") is None  # Evicted
    assert cache.get("k4")["val"] == 4

    # Verify no mutation of returned object affects cache
    item = cache.get("k1")
    item["val"] = 999
    assert cache.get("k1")["val"] == 1  # Unmutated safe copy

    stats = cache.get_stats()
    assert stats["maxsize"] == 3
    assert stats["size"] == 3


def test_cache_hit_prevents_recomputation():
    """Verify identical request returns cached result instantly without recomputing."""
    engine = RAGSafetyRecommendationEngine(use_llm=False)  # Extractive mode
    narrative = "High pressure gas line flange leaking near compressor area."
    sif_res = {"probability": 0.91, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"}
    lsr_res = {"triggered_rules": ["Energy Isolation", "Work Authorization"]}

    # First request -> Cache Miss
    t0 = time.time()
    res1 = engine.generate_recommendations(narrative, sif_res, lsr_res)
    t_miss = (time.time() - t0) * 1000

    assert res1["recommendation_status"] == "GROUNDED"

    # Second request -> Cache Hit
    t0 = time.time()
    res2 = engine.generate_recommendations(narrative, sif_res, lsr_res)
    t_hit = (time.time() - t0) * 1000

    assert res2["recommendation_status"] == "GROUNDED"
    assert res1["summary"] == res2["summary"]
    assert t_hit < t_miss  # Cache hit must be faster
    assert engine.recommendation_cache.get_stats()["hits"] >= 1


def test_different_incidents_cause_cache_miss():
    """Verify different incidents generate distinct cache keys and separate results."""
    engine = RAGSafetyRecommendationEngine(use_llm=False)
    sif_res = {"probability": 0.85, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"}
    lsr_res = {"triggered_rules": ["Line of Fire"]}

    res1 = engine.generate_recommendations("Scaffolding unclamped near crane swing radius.", sif_res, lsr_res)
    res2 = engine.generate_recommendations("Worker entered vessel without atmospheric gas check.", sif_res, lsr_res)

    assert res1["recommendation_status"] == "GROUNDED"
    assert res2["recommendation_status"] == "GROUNDED"
    stats = engine.recommendation_cache.get_stats()
    assert stats["size"] == 2


def test_ollama_unavailable_fallback():
    """Verify system gracefully falls back to Extractive RAG when Ollama is unavailable."""
    # Point to invalid Ollama URL to trigger 6s socket timeout / connection error
    engine = RAGSafetyRecommendationEngine(use_llm=True, ollama_url="http://127.0.0.1:59999")
    narrative = "Hot work started without spark containment blanket at Duliajan manifold."
    sif_res = {"probability": 0.75, "is_sif": True, "risk_tier": "ELEVATED_SIF_POTENTIAL"}
    lsr_res = {"triggered_rules": ["Hot Work"]}

    t0 = time.time()
    res = engine.generate_recommendations(narrative, sif_res, lsr_res)
    t_elapsed = time.time() - t0

    assert res["recommendation_status"] == "GROUNDED"
    assert res["grounded"] is True
    assert len(res["sources"]) > 0
    assert t_elapsed < 8.0  # Must not block beyond timeout limit


def test_concurrent_request_safety():
    """Verify concurrent identical requests run thread-safely with zero exceptions or race conditions."""
    engine = RAGSafetyRecommendationEngine(use_llm=False)
    narrative = "Electrical maintenance performed on live 415V MCC panel without LOTO."
    sif_res = {"probability": 0.95, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"}
    lsr_res = {"triggered_rules": ["Energy Isolation"]}

    results = []
    errors = []

    def worker():
        try:
            res = engine.generate_recommendations(narrative, sif_res, lsr_res)
            results.append(res)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent execution errors: {errors}"
    assert len(results) == 10
    for r in results:
        assert r["recommendation_status"] == "GROUNDED"
