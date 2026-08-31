"""
metadata.py - Document and Chunk Metadata Management for Stage 16 RAG.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import json
from pathlib import Path


class DocumentMetadata(BaseModel):
    filename: str = Field(..., description="Source PDF filename.")
    title: str = Field(..., description="Document title extracted or fallback.")
    path: str = Field(..., description="Absolute or relative file path.")
    total_pages: int = Field(..., description="Total pages in PDF.")
    pages_with_text: int = Field(..., description="Count of pages containing extracted text.")
    pages_without_text: int = Field(..., description="Count of empty pages.")
    characters_extracted: int = Field(..., description="Total character count extracted.")


class ChunkMetadata(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk tracking ID, e.g. doc_p12_c01")
    document: str = Field(..., description="Source document filename")
    page: int = Field(..., description="1-indexed page number")
    section: str = Field(default="General", description="Section heading or topic label")
    text: str = Field(..., description="Extracted semantic text snippet")
    start_char: int = Field(default=0, description="Start character offset in document text")
    end_char: int = Field(default=0, description="End character offset in document text")


class SourceCitation(BaseModel):
    document: str = Field(..., description="Source reference document filename")
    page: int = Field(..., description="Page number of retrieved reference")
    section: str = Field(default="General", description="Section header")
    chunk_id: str = Field(..., description="Unique ID of source passage")
    similarity: float = Field(default=0.0, description="Cosine similarity score")
    snippet: str = Field(default="", description="Relevant supporting text passage snippet")


def save_json(data: Any, filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Any:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
