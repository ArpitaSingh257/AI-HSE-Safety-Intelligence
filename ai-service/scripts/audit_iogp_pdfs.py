"""
audit_iogp_pdfs.py - In-depth audit and inspection of all 4 IOGP PDF files.
Reads every page, analyzes section headers, table structures, narrative blocks,
identifies exact incident count and page numbers, and dumps raw text for verification.
"""

import os
import re
import json
from pathlib import Path

def extract_pdf_pages_clean(pdf_path):
    pages = []
    
    # Try pypdf / pypdf2 / pdfplumber / fitz
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append((idx + 1, text))
        return pages, "pypdf"
    except Exception as e:
        pass

    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        for idx, page in enumerate(doc):
            text = page.get_text() or ""
            pages.append((idx + 1, text))
        return pages, "fitz"
    except Exception as e:
        pass

    try:
        import pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            for idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append((idx + 1, text))
        return pages, "pdfplumber"
    except Exception as e:
        pass

    try:
        import pypdf2
        reader = pypdf2.PdfReader(str(pdf_path))
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append((idx + 1, text))
        return pages, "pypdf2"
    except Exception as e:
        pass

    return [], "none"

def analyze_pdf_content(pdf_path, name):
    pages, method = extract_pdf_pages_clean(pdf_path)
    total_pages = len(pages)
    
    print(f"\n=======================================================")
    print(f"AUDITING: {name} ({pdf_path.name})")
    print(f"Total Pages: {total_pages} (Method: {method})")
    print(f"=======================================================")
    
    incident_candidates = []
    page_summaries = []
    
    for page_num, text in pages:
        clean_text = text.strip()
        line_count = len(clean_text.splitlines())
        word_count = len(clean_text.split())
        
        # Check for incident identifiers
        # Examples: "Incident #", "Case Study", "Event #", "What happened", "Description of event", "Fatal incident", "High potential"
        has_narrative_header = bool(re.search(r'(what happened|description of event|incident description|event description|what went wrong|narrative)', clean_text, re.I))
        has_causal_header = bool(re.search(r'(causal factors|causes|corrective actions|lessons learned|recommendations)', clean_text, re.I))
        has_lsr = bool(re.search(r'(life[- ]saving rule|life saving rule)', clean_text, re.I))
        has_fatal_word = bool(re.search(r'\b(fatal|fatality|fatalities|died|killed|deceased)\b', clean_text, re.I))
        has_hipo_word = bool(re.search(r'\b(high potential|hipo|hpe)\b', clean_text, re.I))
        
        is_table_only = word_count > 30 and (clean_text.count('\t') > 10 or len(re.findall(r'\b\d{1,3}(?:\.\d+)?%?\b', clean_text)) > word_count * 0.4)
        
        classification = "BENCHMARK_TABLE / STATS" if is_table_only else "TEXT_CONTENT"
        
        if has_narrative_header or (has_fatal_word and line_count > 5) or (has_hipo_word and has_causal_header):
            classification = "INCIDENT_NARRATIVE_CANDIDATE"
            incident_candidates.append({
                "page": page_num,
                "word_count": word_count,
                "has_narrative_header": has_narrative_header,
                "has_causal_header": has_causal_header,
                "has_lsr": has_lsr,
                "has_fatal": has_fatal_word,
                "has_hipo": has_hipo_word,
                "preview": clean_text[:200].replace('\n', ' ')
            })
            
        page_summaries.append({
            "page": page_num,
            "word_count": word_count,
            "classification": classification
        })
        
    print(f"Total Incident Narrative Candidates Found: {len(incident_candidates)}")
    for cand in incident_candidates:
        print(f"  - Page {cand['page']}: words={cand['word_count']}, narrative_hdr={cand['has_narrative_header']}, lsr={cand['has_lsr']}, fatal={cand['has_fatal']}, hipo={cand['has_hipo']}")
        print(f"    Preview: {cand['preview']}...\n")
        
    return {
        "filename": pdf_path.name,
        "total_pages": total_pages,
        "total_candidates": len(incident_candidates),
        "candidates": incident_candidates,
        "pages": pages
    }

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    resources_dir = base_dir / "resources"
    audit_dump_dir = base_dir / "ai-service" / "datasets" / "quality" / "iogp_audit_dumps"
    audit_dump_dir.mkdir(parents=True, exist_ok=True)
    
    files = {
        "IOGP_HPE": resources_dir / "IAOGP - High Potential Event Reports.pdf",
        "IOGP_FATAL": resources_dir / "IAOGP - Safety performance indicators.pdf",
        "IOGP_SPI_2025": resources_dir / "IAOGP-Safety performance indicators - 2025 data.pdf",
        "IOGP_GUIDE": resources_dir / "IAOGP - Safety data reporting user guide.pdf"
    }
    
    audit_results = {}
    for tag, path in files.items():
        if path.exists():
            res = analyze_pdf_content(path, tag)
            audit_results[tag] = {
                "filename": res["filename"],
                "total_pages": res["total_pages"],
                "candidate_count": res["total_candidates"],
                "candidates": res["candidates"]
            }
            # Dump full text
            with open(audit_dump_dir / f"{tag}_full_text_pages.json", "w", encoding="utf-8") as f:
                json.dump([{"page": p[0], "text": p[1]} for p in res["pages"]], f, indent=2)
        else:
            print(f"File not found: {path}")
            
    with open(audit_dump_dir / "audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
        
    print("\nAudit Summary saved to", audit_dump_dir)

if __name__ == "__main__":
    main()
