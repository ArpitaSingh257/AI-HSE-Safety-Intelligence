"""
document_loader.py - Robust PDF Extraction and Source Inventory Generation for OILPS.
Extracts text page-by-page, preserving page numbers, section headers, and metadata.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Try pdfplumber first, fallback to pypdf
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.metadata import DocumentMetadata, save_json

logger = logging.getLogger("OILPS_DocumentLoader")
logging.basicConfig(level=logging.INFO)


def discover_pdf_resources(target_dir: Path = None) -> List[Path]:
    """
    Locate the 5 approved safety reference PDFs.
    Checks target directory or candidate directories in order.
    """
    search_paths = []
    if target_dir:
        search_paths.append(Path(target_dir))
        
    project_root = BASE_DIR.parent
    search_paths.extend([
        BASE_DIR / "resources" / "safety-recommendation-engine",
        BASE_DIR / "resources" / "Safety_recommendation_engine",
        project_root / "resources" / "Safety_recommendation_engine",
        project_root / "resources"
    ])

    found_pdfs = []
    src_dir_used = None

    for candidate in search_paths:
        if candidate.exists() and candidate.is_dir():
            pdfs = sorted(list(candidate.glob("*.pdf")))
            # We look for the 5 safety recommendation engine PDFs specifically
            target_names = [
                "IOGP Life-Saving Rules.pdf",
                "Process Safety Fundamentals.pdf",
                "Safety performance indicators – 2023 data.pdf",
                "Safety performance indicators – 2024 data.pdf",
                "Safety performance indicators – 2025 data.pdf"
            ]
            
            # Case-insensitive / normalized check
            matched = []
            for pdf in pdfs:
                if any(t.lower().replace(" ", "").replace("–", "-") in pdf.name.lower().replace(" ", "").replace("–", "-") for t in target_names):
                    matched.append(pdf)
                    
            if len(matched) >= 5 or (len(matched) > 0 and len(found_pdfs) == 0):
                found_pdfs = matched
                src_dir_used = candidate
                break

    # Ensure target directory ai-service/resources/safety-recommendation-engine exists and has copies
    dest_dir = BASE_DIR / "resources" / "safety-recommendation-engine"
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied_pdfs = []
    for pdf in found_pdfs:
        target_path = dest_dir / pdf.name
        if not target_path.exists():
            shutil.copy2(pdf, target_path)
        copied_pdfs.append(target_path)

    return copied_pdfs if copied_pdfs else found_pdfs


def extract_page_text_pdfplumber(pdf_path: Path) -> List[Tuple[int, str]]:
    """Extract page text using pdfplumber."""
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            results.append((idx, text.strip()))
    return results


def extract_page_text_pypdf(pdf_path: Path) -> List[Tuple[int, str]]:
    """Extract page text using pypdf fallback."""
    results = []
    reader = pypdf.PdfReader(str(pdf_path))
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        results.append((idx, text.strip()))
    return results


def extract_pdf_document(pdf_path: Path) -> Dict[str, Any]:
    """
    Extract a single PDF with page metadata and section hints.
    Returns structured document inventory.
    """
    pdf_path = Path(pdf_path)
    filename = pdf_path.name
    doc_title = pdf_path.stem.replace("_", " ").replace("-", " ")

    pages_data = []
    extraction_error = None

    try:
        if HAS_PDFPLUMBER:
            raw_pages = extract_page_text_pdfplumber(pdf_path)
        elif HAS_PYPDF:
            raw_pages = extract_page_text_pypdf(pdf_path)
        else:
            raise ImportError("Neither pdfplumber nor pypdf is installed.")
    except Exception as e:
        logger.warning(f"Primary PDF extraction failed for {filename}: {e}. Retrying with fallback...")
        try:
            if HAS_PYPDF:
                raw_pages = extract_page_text_pypdf(pdf_path)
            else:
                raise e
        except Exception as e2:
            extraction_error = str(e2)
            raw_pages = []

    pages_with_text = 0
    pages_without_text = 0
    total_chars = 0

    for page_num, text in raw_pages:
        char_count = len(text)
        total_chars += char_count
        if char_count > 0:
            pages_with_text += 1
        else:
            pages_without_text += 1

        # Simple heuristic for section title extraction on page
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        section_heading = "General"
        if lines:
            first_line = lines[0]
            if len(first_line) < 80 and not first_line.endswith("."):
                section_heading = first_line

        pages_data.append({
            "page": page_num,
            "section": section_heading,
            "character_count": char_count,
            "text": text
        })

    metadata = DocumentMetadata(
        filename=filename,
        title=doc_title,
        path=str(pdf_path.resolve()),
        total_pages=len(raw_pages),
        pages_with_text=pages_with_text,
        pages_without_text=pages_without_text,
        characters_extracted=total_chars
    )

    return {
        "metadata": metadata.model_dump(),
        "pages": pages_data,
        "extraction_error": extraction_error
    }


class DocumentLoader:
    """Production PDF Ingestion & Source Inventory Loader."""

    def __init__(self, resource_dir: Path = None):
        self.resource_dir = resource_dir
        self.output_dir = BASE_DIR / "datasets" / "rag"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_corpus(self) -> Dict[str, Any]:
        """
        Extract all 5 safety PDFs and build reproducible corpus inventory.
        """
        pdfs = discover_pdf_resources(self.resource_dir)
        logger.info(f"Discovered {len(pdfs)} approved safety reference PDFs.")

        corpus = {
            "summary": {
                "total_documents": len(pdfs),
                "total_pages": 0,
                "total_characters": 0
            },
            "documents": []
        }

        for pdf in pdfs:
            logger.info(f"Extracting {pdf.name}...")
            doc_obj = extract_pdf_document(pdf)
            meta = doc_obj["metadata"]
            corpus["summary"]["total_pages"] += meta["total_pages"]
            corpus["summary"]["total_characters"] += meta["characters_extracted"]
            corpus["documents"].append(doc_obj)

        # Save to datasets/rag/extracted_corpus.json
        save_json(corpus, self.output_dir / "extracted_corpus.json")
        logger.info(f"Extracted corpus saved to {self.output_dir / 'extracted_corpus.json'}")
        return corpus


if __name__ == "__main__":
    loader = DocumentLoader()
    res = loader.load_corpus()
    print("Corpus summary:", res["summary"])
