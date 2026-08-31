"""
evaluate_rag.py - Retrieval & Grounding Benchmark Evaluation Script for Stage 16.
Calculates Recall@K, Precision@K, and MRR across safety query benchmarks and verifies demo scenarios.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.retriever import VectorRetriever
from rag.grounded_recommender import RAGSafetyRecommendationEngine
from knowledge.ingest_pipeline import run_rag_ingestion

logger = logging.getLogger("OILPS_RAGEval")
logging.basicConfig(level=logging.INFO)

EVAL_GROUND_TRUTH = [
    {
        "query_id": "Q1_ENERGY_ISOLATION",
        "query": "hydrostatic test pressure line isolation bleeder valve plug rupture",
        "expected_documents": ["IOGP Life-Saving Rules.pdf", "Process Safety Fundamentals.pdf"],
        "expected_keywords": ["isolation", "pressure", "line", "energy"]
    },
    {
        "query_id": "Q2_LIFTING_OPERATIONS",
        "query": "crane rigging suspended load line of fire mechanical lift swing",
        "expected_documents": ["IOGP Life-Saving Rules.pdf", "Process Safety Fundamentals.pdf"],
        "expected_keywords": ["lift", "crane", "rigging", "suspended"]
    },
    {
        "query_id": "Q3_CONFINED_SPACE_GAS",
        "query": "confined space toxic gas h2s vessel entry atmospheric testing gas detector",
        "expected_documents": ["IOGP Life-Saving Rules.pdf", "Process Safety Fundamentals.pdf"],
        "expected_keywords": ["confined", "space", "gas", "toxic"]
    },
    {
        "query_id": "Q4_WORKING_AT_HEIGHT",
        "query": "fall arrest harness scaffold safety belt working at height elevated platform",
        "expected_documents": ["IOGP Life-Saving Rules.pdf", "Process Safety Fundamentals.pdf"],
        "expected_keywords": ["height", "harness", "scaffold", "fall"]
    },
    {
        "query_id": "Q5_SAFETY_INDICATORS",
        "query": "fatalities total recordable injury frequency rate safety performance data reporting",
        "expected_documents": [
            "Safety performance indicators – 2023 data.pdf",
            "Safety performance indicators – 2024 data.pdf",
            "Safety performance indicators – 2025 data.pdf"
        ],
        "expected_keywords": ["fatalities", "safety", "data", "reporting", "performance"]
    }
]


def evaluate_retrieval(k: int = 5) -> Dict[str, float]:
    """Calculate Recall@K, Precision@K, and MRR for VectorRetriever."""
    retriever = VectorRetriever()
    retriever.load_index()

    recalls = []
    precisions = []
    reciprocal_ranks = []

    for item in EVAL_GROUND_TRUTH:
        q_text = item["query"]
        expected_docs = set(item["expected_documents"])

        retrieved = retriever.retrieve(q_text, top_k=k, min_confidence=0.10)
        retrieved_docs = [r["document"] for r in retrieved]

        hits = [1 if doc in expected_docs else 0 for doc in retrieved_docs]
        unique_hits = set(retrieved_docs).intersection(expected_docs)

        # Recall@K: fraction of expected documents retrieved
        recall = len(unique_hits) / len(expected_docs) if expected_docs else 0.0
        # Precision@K: fraction of retrieved items that match expected documents
        precision = sum(hits) / k if k > 0 else 0.0

        # MRR: reciprocal of rank of first relevant result
        rr = 0.0
        for rank, doc in enumerate(retrieved_docs, start=1):
            if doc in expected_docs:
                rr = 1.0 / rank
                break

        recalls.append(recall)
        precisions.append(precision)
        reciprocal_ranks.append(rr)

    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0
    mean_precision = sum(precisions) / len(precisions) if precisions else 0.0
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0

    return {
        f"Recall@{k}": round(mean_recall, 4),
        f"Precision@{k}": round(mean_precision, 4),
        "MRR": round(mrr, 4)
    }


def evaluate_demo_scenarios() -> Dict[str, Any]:
    """Test the 4 required demo scenarios (A, B, C, D)."""
    engine = RAGSafetyRecommendationEngine()

    scenarios = {
        "Scenario_A_Hydrotest": {
            "narrative": "Operator attempted to tighten a fitting while a high-pressure line remained pressurized at 4500 psi. Bleeder plug ruptured.",
            "sif": {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
            "lsr": {"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"]}
        },
        "Scenario_B_Crane_Lifting": {
            "narrative": "During crane lifting operations, the rigger walked underneath the suspended pipe load. The sling snapped.",
            "sif": {"probability": 0.76, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
            "lsr": {"triggered_rules": ["Safe Mechanical Lifting", "Line of Fire"]}
        },
        "Scenario_C_Confined_Space_H2S": {
            "narrative": "Entrant stepped into vessel for inspection without toxic gas testing. High H2S concentration detected.",
            "sif": {"probability": 0.92, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
            "lsr": {"triggered_rules": ["Confined Space", "Toxic Gas / Hazardous Substance"]}
        },
        "Scenario_D_Minor_Slip": {
            "narrative": "Worker slipped on wet floor near office entrance and sustained minor elbow bruise.",
            "sif": {"probability": 0.04, "is_sif": False, "risk_tier": "LOW_POTENTIAL_INCIDENT"},
            "lsr": {"triggered_rules": []}
        }
    }

    results = {}
    for name, data in scenarios.items():
        rec = engine.generate_recommendations(
            narrative=data["narrative"],
            sif_result=data["sif"],
            lsr_result=data["lsr"]
        )
        results[name] = {
            "status": rec["recommendation_status"],
            "grounded": rec["grounded"],
            "priority": rec["priority"],
            "sources_count": len(rec["sources"]),
            "summary_preview": rec["summary"][:120] + "..."
        }

    return results


def run_full_evaluation():
    logger.info("Ensuring RAG vector index is built...")
    run_rag_ingestion()

    logger.info("=== RETRIEVAL EVALUATION METRICS ===")
    metrics = evaluate_retrieval(k=5)
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    logger.info("=== DEMO SCENARIO EVALUATION ===")
    demo_res = evaluate_demo_scenarios()
    for sc, res in demo_res.items():
        print(f"  [{sc}]: status={res['status']}, priority={res['priority']}, sources={res['sources_count']}")

    return {"retrieval_metrics": metrics, "demo_scenarios": demo_res}


if __name__ == "__main__":
    run_full_evaluation()
