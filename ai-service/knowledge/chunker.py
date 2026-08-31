"""
chunker.py - Semantic Chunking Engine for OILPS RAG Pipeline.
Splits extracted document pages into section-aware, traceable semantic chunks with overlap.
"""

import sys
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.metadata import ChunkMetadata, save_json, load_json

logger = logging.getLogger("OILPS_Chunker")
logging.basicConfig(level=logging.INFO)


class SemanticChunker:
    """
    Semantic Chunker for Safety Guidance Documents.
    Respects document sections, paragraphs, and page provenance.
    """

    def __init__(self, target_chunk_size: int = 400, overlap: int = 80):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def split_text_into_paragraphs(self, text: str) -> List[str]:
        """Split page text by double newlines or bullet points."""
        raw_paras = re.split(r'\n\s*\n|\n(?=[•\-\*\d+\.])', text)
        clean_paras = [p.strip().replace("\n", " ") for p in raw_paras if p.strip()]
        return clean_paras

    def chunk_document_page(
        self,
        document_name: str,
        page_num: int,
        default_section: str,
        page_text: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a single document page into semantic passages.
        """
        if not page_text.strip():
            return []

        paragraphs = self.split_text_into_paragraphs(page_text)
        chunks = []
        current_chunk_words = []
        current_chunk_len = 0
        current_section = default_section
        chunk_idx = 1

        # Clean document base name for chunk ID
        clean_doc_id = re.sub(r'[^a-zA-Z0-9]', '_', Path(document_name).stem).lower()

        for para in paragraphs:
            # Check if paragraph looks like a section header
            if len(para) < 60 and not para.endswith((".", ":", ";")):
                if current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    cid = f"{clean_doc_id}_p{page_num}_c{chunk_idx:02d}"
                    chunks.append(ChunkMetadata(
                        chunk_id=cid,
                        document=document_name,
                        page=page_num,
                        section=current_section,
                        text=chunk_text
                    ).model_dump())
                    chunk_idx += 1
                    current_chunk_words = []
                    current_chunk_len = 0
                current_section = para

            words = para.split()
            for word in words:
                current_chunk_words.append(word)
                current_chunk_len += len(word) + 1

                if current_chunk_len >= self.target_chunk_size:
                    chunk_text = " ".join(current_chunk_words)
                    cid = f"{clean_doc_id}_p{page_num}_c{chunk_idx:02d}"
                    chunks.append(ChunkMetadata(
                        chunk_id=cid,
                        document=document_name,
                        page=page_num,
                        section=current_section,
                        text=chunk_text
                    ).model_dump())
                    chunk_idx += 1

                    # Keep last few words for overlap
                    overlap_words = current_chunk_words[-10:] if len(current_chunk_words) > 10 else []
                    current_chunk_words = overlap_words
                    current_chunk_len = sum(len(w) + 1 for w in overlap_words)

        # Flush remaining words
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            if len(chunk_text) >= 20: # Ignore tiny noise
                cid = f"{clean_doc_id}_p{page_num}_c{chunk_idx:02d}"
                chunks.append(ChunkMetadata(
                    chunk_id=cid,
                    document=document_name,
                    page=page_num,
                    section=current_section,
                    text=chunk_text
                ).model_dump())

        return chunks

    def process_corpus(self, corpus_json_path: Path = None) -> List[Dict[str, Any]]:
        """
        Process extracted corpus and save semantic chunks.
        """
        if corpus_json_path is None:
            corpus_json_path = BASE_DIR / "datasets" / "rag" / "extracted_corpus.json"

        corpus = load_json(corpus_json_path)
        all_chunks = []

        for doc_obj in corpus.get("documents", []):
            meta = doc_obj["metadata"]
            doc_name = meta["filename"]
            logger.info(f"Chunking document: {doc_name}...")

            for page_obj in doc_obj.get("pages", []):
                p_num = page_obj["page"]
                p_sec = page_obj.get("section", "General")
                p_text = page_obj.get("text", "")

                page_chunks = self.chunk_document_page(
                    document_name=doc_name,
                    page_num=p_num,
                    default_section=p_sec,
                    page_text=p_text
                )
                all_chunks.extend(page_chunks)

        out_path = BASE_DIR / "datasets" / "rag" / "semantic_chunks.json"
        save_json({"total_chunks": len(all_chunks), "chunks": all_chunks}, out_path)
        logger.info(f"Generated {len(all_chunks)} semantic chunks. Saved to {out_path}")
        return all_chunks


if __name__ == "__main__":
    chunker = SemanticChunker()
    chunks = chunker.process_corpus()
    print("Total chunks created:", len(chunks))
