"""
benchmark_llm_generation_stage18.py - Benchmark Script for Stage 18 LLM Latency & Grounding.
Measures retrieval, reranking, prompt construction, LLM generation time, token counts, and grounding rates.
"""

import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.safety_pipeline import SafetyPipeline
from rag.grounded_recommender import RAGSafetyRecommendationEngine
from rag.context_builder import SafetyContextBuilder
from rag.retriever import VectorRetriever
from rag.reranker import SafetyReranker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Stage18Benchmark")

SCENARIOS = {
    "Scenario_1_Hydrotest": {
        "name": "Scenario 1 — Hydrotest / Pressure",
        "narrative": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.",
    },
    "Scenario_2_Crane_Lifting": {
        "name": "Scenario 2 — Crane / Lifting",
        "narrative": "During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby.",
    },
    "Scenario_3_Confined_Space_H2S": {
        "name": "Scenario 3 — Confined Space + H2S",
        "narrative": "During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space.",
    },
    "Scenario_4_Minor_Slip": {
        "name": "Scenario 4 — Minor Slip Negative Control",
        "narrative": "An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred and no hazardous energy or process safety condition was involved.",
    }
}


def run_benchmark_stage18():
    logger.info("=== STAGE 18 BENCHMARKING LLM GENERATION & LATENCY ===")
    pipeline = SafetyPipeline()
    rec_engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")

    results = []

    for key, sc in SCENARIOS.items():
        narrative = sc["narrative"]
        logger.info(f"\n--- BENCHMARKING: {sc['name']} ---")

        t0 = time.time()
        raw_res = pipeline.analyze_incident(narrative)
        t_infer = time.time() - t0

        sif_data = raw_res["sif"]
        lsr_data = raw_res["life_saving_rules"]

        t_gen_0 = time.time()
        rec_data = rec_engine.generate_recommendations(
            narrative=narrative,
            sif_result={"probability": sif_data["probability"], "is_sif": bool(sif_data["label"] == 1), "risk_tier": raw_res["risk_tier"], "threshold": sif_data["threshold"]},
            lsr_result={"triggered_rules": lsr_data.get("predicted_rules", []), "probabilities": lsr_data["probabilities"]}
        )
        t_gen = time.time() - t_gen_0

        results.append({
            "scenario": sc["name"],
            "status": rec_data.get("recommendation_status"),
            "priority": rec_data.get("priority"),
            "inference_time": round(t_infer, 3),
            "generation_time": round(t_gen, 3),
            "sources_count": len(rec_data.get("sources", [])),
            "summary_snippet": rec_data.get("summary", "")[:100]
        })

        print(f"[{sc['name']}] Status: {rec_data.get('recommendation_status')} | Priority: {rec_data.get('priority')} | LLM Time: {t_gen:.2f}s")

    return results


if __name__ == "__main__":
    run_benchmark_stage18()
