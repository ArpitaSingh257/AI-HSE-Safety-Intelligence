"""
test_single_ollama_query.py - Benchmark timing for a single Ollama RAG query.
"""

import sys
import time
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.grounded_recommender import RAGSafetyRecommendationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OllamaTimingTest")


def run_single_query_benchmark(model_name: str = "llama3.2:1b", timeout_seconds: float = 60.0):
    logger.info(f"Initializing RAG Recommendation Engine (Target Model: '{model_name}', Timeout: {timeout_seconds}s)...")
    
    # Initialize engine with custom timeout & model
    engine = RAGSafetyRecommendationEngine(ollama_model=model_name)
    
    narrative = "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured."
    sif_result = {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"}
    lsr_result = {"triggered_rules": ["Energy Isolation"]}

    logger.info("=== STARTING SINGLE QUERY BENCHMARK ===")
    logger.info(f"Incident Narrative: {narrative[:80]}...")

    start_time = time.time()
    
    try:
        recommendations = engine.generate_recommendations(
            narrative=narrative,
            sif_result=sif_result,
            lsr_result=lsr_result
        )
        elapsed = time.time() - start_time
        
        logger.info(f"=== BENCHMARK COMPLETED IN {elapsed:.2f} SECONDS ===")
        logger.info(f"Status: {recommendations.get('recommendation_status')}")
        logger.info(f"Priority: {recommendations.get('priority')}")
        logger.info(f"Summary: {recommendations.get('summary')[:120]}...")
        logger.info(f"Immediate Actions ({len(recommendations.get('immediate_actions', []))}): {recommendations.get('immediate_actions')[:2]}")
        logger.info(f"Sources ({len(recommendations.get('sources', []))}): {[s['document'] + ' (p.' + str(s['page']) + ')' for s in recommendations.get('sources', [])]}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Benchmark failed after {elapsed:.2f} seconds with error: {e}")


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:1b"
    run_single_query_benchmark(model_name=model)
