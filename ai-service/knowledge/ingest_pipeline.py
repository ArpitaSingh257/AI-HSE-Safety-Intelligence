"""
ingest_pipeline.py - Reproducible End-to-End PDF Ingestion & Indexing Pipeline for Stage 16.
"""

import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.document_loader import DocumentLoader
from knowledge.chunker import SemanticChunker
from rag.retriever import VectorRetriever

logger = logging.getLogger("OILPS_IngestPipeline")
logging.basicConfig(level=logging.INFO)


def run_rag_ingestion() -> dict:
    """
    Execute full RAG ingestion pipeline:
    Extract PDFs -> Semantic Chunking -> Vector Store Indexing.
    """
    logger.info("=== STEP 1: PDF DOCUMENT EXTRACTION ===")
    loader = DocumentLoader()
    corpus = loader.load_corpus()

    logger.info("=== STEP 2: SEMANTIC CHUNKING ===")
    chunker = SemanticChunker()
    chunks = chunker.process_corpus()

    logger.info("=== STEP 3: EMBEDDING & FAISS INDEXING ===")
    retriever = VectorRetriever()
    retriever.build_index(chunks)

    logger.info("=== RAG INGESTION PIPELINE COMPLETED SUCCESSFULLY ===")
    return {
        "documents": corpus["summary"]["total_documents"],
        "pages": corpus["summary"]["total_pages"],
        "characters": corpus["summary"]["total_characters"],
        "chunks": len(chunks),
        "index_ready": True
    }


if __name__ == "__main__":
    summary = run_rag_ingestion()
    print("Ingestion summary:", summary)
