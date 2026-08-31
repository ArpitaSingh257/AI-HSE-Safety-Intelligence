"""
reranker.py - Modular Reranking Engine for OILPS Safety Retrieval.
Refines vector search results using hazard-domain keyword boost and semantic relevance scoring.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("OILPS_Reranker")


class SafetyReranker:
    """
    Lightweight Domain-Aware Reranker for Precursor Safety Guidance.
    """

    def __init__(self, hazard_boost_weight: float = 0.25):
        self.hazard_boost_weight = hazard_boost_weight
        # Critical HSE hazard keywords to boost in reranking
        self.hazard_keywords = [
            "isolation", "isolated", "lockout", "tagout", "pressure", "hydrostatic",
            "bleeder", "valve", "confined space", "permit", "lifting", "crane", "rigging", "hoist",
            "line of fire", "toxic gas", "h2s", "breathing apparatus", "harness", "scaffold", "height"
        ]

    def rerank(self, query: str, retrieved_passages: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank retrieved passages using vector similarity + domain keyword match density.
        """
        if not retrieved_passages:
            return []

        query_terms = set(re.findall(r'\b\w+\b', query.lower()))
        reranked = []

        for item in retrieved_passages:
            text_lower = item["text"].lower()
            orig_sim = item.get("similarity", 0.0)

            # Keyword overlap score
            text_terms = set(re.findall(r'\b\w+\b', text_lower))
            overlap = len(query_terms.intersection(text_terms))
            overlap_score = overlap / (len(query_terms) + 1e-5)

            # Domain hazard keyword boost
            hazard_hits = sum(1 for kw in self.hazard_keywords if kw in text_lower and kw in query.lower())
            hazard_boost = min(0.3, hazard_hits * 0.1)

            final_score = orig_sim + (self.hazard_boost_weight * overlap_score) + hazard_boost
            
            enhanced_item = dict(item)
            enhanced_item["rerank_score"] = round(final_score, 4)
            reranked.append(enhanced_item)

        # Sort descending by final rerank_score with stable tie-breaker
        reranked.sort(key=lambda x: (x["rerank_score"], x.get("document", ""), x.get("page", 0), x.get("chunk_id", "")), reverse=True)
        return reranked[:top_n]
