"""
test_rag_ingestion.py - QA Tests for Stage 16 PDF Ingestion & Corpus Extraction.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.document_loader import DocumentLoader, discover_pdf_resources, extract_pdf_document
from knowledge.chunker import SemanticChunker
from knowledge.metadata import load_json


def test_discover_five_pdfs():
    """Verify all five approved safety reference PDFs are discovered."""
    pdfs = discover_pdf_resources()
    assert len(pdfs) >= 5, f"Expected 5 PDFs, found {len(pdfs)}"
    filenames = [p.name for p in pdfs]
    assert any("Life-Saving" in f for f in filenames)
    assert any("Fundamentals" in f for f in filenames)
    assert any("2023" in f for f in filenames)
    assert any("2024" in f for f in filenames)
    assert any("2025" in f for f in filenames)


def test_pdf_extraction_metadata():
    """Verify PDF extraction preserves page numbers, text, and metadata."""
    pdfs = discover_pdf_resources()
    doc_data = extract_pdf_document(pdfs[0])

    meta = doc_data["metadata"]
    assert meta["total_pages"] > 0
    assert meta["characters_extracted"] > 0
    assert meta["pages_with_text"] > 0
    assert len(doc_data["pages"]) == meta["total_pages"]

    # Check 1-indexed page numbering
    for page_obj in doc_data["pages"]:
        assert page_obj["page"] >= 1
        assert "section" in page_obj


def test_semantic_chunker():
    """Verify semantic chunking generates valid chunks with required schema."""
    loader = DocumentLoader()
    corpus = loader.load_corpus()

    chunker = SemanticChunker()
    chunks = chunker.process_corpus()

    assert len(chunks) > 0
    sample_chunk = chunks[0]

    required_keys = ["chunk_id", "document", "page", "section", "text"]
    for key in required_keys:
        assert key in sample_chunk, f"Missing required key '{key}' in chunk schema"

    assert sample_chunk["page"] >= 1
    assert len(sample_chunk["text"]) > 0
