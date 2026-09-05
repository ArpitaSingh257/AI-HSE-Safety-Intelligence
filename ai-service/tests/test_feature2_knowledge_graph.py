"""
test_feature2_knowledge_graph.py - Comprehensive Unit Tests for Graph RAG Lineage Visualizer
"""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from services.graph_service import KnowledgeGraphService

@pytest.fixture
def graph_service():
    return KnowledgeGraphService()

def test_graph_lineage_topology_structure(graph_service):
    res = graph_service.get_lineage_graph()
    assert res["status"] in ["SUCCESS", "FALLBACK"]
    assert "nodes" in res
    assert "edges" in res
    assert "metrics" in res
    
    nodes = res["nodes"]
    edges = res["edges"]
    metrics = res["metrics"]
    
    assert len(nodes) > 0
    assert len(edges) > 0
    assert metrics["total_nodes"] == len(nodes)
    assert metrics["total_edges"] == len(edges)

def test_graph_filtering_by_site(graph_service):
    res = graph_service.get_lineage_graph(site_filter="Duliajan")
    assert res["status"] in ["SUCCESS", "FALLBACK"]
    assert len(res["nodes"]) > 0

def test_graph_node_schema_integrity(graph_service):
    res = graph_service.get_lineage_graph()
    for n in res["nodes"]:
        assert "id" in n
        assert "label" in n
        assert "type" in n
        assert "category" in n
        assert "risk_score" in n
        assert "details" in n
        assert isinstance(n["risk_score"], float)
