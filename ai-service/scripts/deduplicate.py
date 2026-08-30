"""
deduplicate.py - Exact and near-duplicate detection and logging for OILPS safety dataset.
Generates:
- datasets/quality/deduplication_report.md
- datasets/processed/oilps_unified_deduped.csv
"""

import os
import re
import csv
import json
import hashlib
from pathlib import Path
from collections import defaultdict

def normalize_text_for_comparison(text):
    if not text:
        return ""
    # Lowercase, remove punctuation and extra whitespace
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = [w for w in text.split() if len(w) > 2]
    return " ".join(tokens)

def get_shingles(text, k=3):
    words = text.split()
    if len(words) < k:
        return set([" ".join(words)])
    return set([" ".join(words[i:i+k]) for i in range(len(words) - k + 1)])

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def run_deduplication(input_unified_csv, output_deduped_csv, report_md_path):
    input_unified_csv = Path(input_unified_csv)
    output_deduped_csv = Path(output_deduped_csv)
    report_md_path = Path(report_md_path)
    
    output_deduped_csv.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    
    records = []
    with open(input_unified_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            records.append(r)
            
    total_records = len(records)
    print(f"Total input records for deduplication: {total_records}")
    
    # 1. Exact Duplicate Detection (Hash on normalized narrative)
    exact_hash_map = defaultdict(list)
    for idx, r in enumerate(records):
        narrative = r.get("narrative", "")
        norm = normalize_text_for_comparison(narrative)
        if len(norm) > 10:
            h = hashlib.md5(norm.encode('utf-8')).hexdigest()
            exact_hash_map[h].append(idx)
        else:
            # If narrative is too short or empty, group by source record ID
            src_id = f"{r.get('source')}_{r.get('source_record_id')}"
            exact_hash_map[src_id].append(idx)
            
    exact_dup_indices_to_remove = set()
    exact_dup_logs = []
    
    for h, group in exact_hash_map.items():
        if len(group) > 1:
            primary_idx = group[0]
            for dup_idx in group[1:]:
                exact_dup_indices_to_remove.add(dup_idx)
                exact_dup_logs.append({
                    "primary_record_id": records[primary_idx]["record_id"],
                    "duplicate_record_id": records[dup_idx]["record_id"],
                    "source": records[dup_idx]["source"],
                    "reason": "Exact narrative text match",
                    "preview": records[primary_idx]["narrative"][:120] + "..."
                })
                
    print(f"Exact duplicates identified: {len(exact_dup_indices_to_remove)}")
    
    # 2. Filter out exact duplicates for near-duplicate scan
    active_indices = [i for i in range(total_records) if i not in exact_dup_indices_to_remove]
    
    # 3. Near Duplicate Detection (Jaccard similarity on 3-word shingles with threshold >= 0.85)
    near_dup_logs = []
    near_dup_indices_to_remove = set()
    
    # Pre-calculate shingles
    shingles_cache = {}
    for idx in active_indices:
        norm = normalize_text_for_comparison(records[idx].get("narrative", ""))
        shingles_cache[idx] = get_shingles(norm, k=3)
        
    for i_pos in range(len(active_indices)):
        idx_a = active_indices[i_pos]
        if idx_a in near_dup_indices_to_remove:
            continue
        shingles_a = shingles_cache[idx_a]
        if not shingles_a:
            continue
            
        for j_pos in range(i_pos + 1, min(i_pos + 200, len(active_indices))):
            idx_b = active_indices[j_pos]
            if idx_b in near_dup_indices_to_remove:
                continue
            shingles_b = shingles_cache[idx_b]
            
            sim = jaccard_similarity(shingles_a, shingles_b)
            if sim >= 0.85:
                near_dup_indices_to_remove.add(idx_b)
                near_dup_logs.append({
                    "primary_record_id": records[idx_a]["record_id"],
                    "duplicate_record_id": records[idx_b]["record_id"],
                    "source_a": records[idx_a]["source"],
                    "source_b": records[idx_b]["source"],
                    "similarity_score": round(sim, 3),
                    "reason": f"Near-duplicate narrative (Jaccard = {sim:.2f})",
                    "preview_a": records[idx_a]["narrative"][:100] + "...",
                    "preview_b": records[idx_b]["narrative"][:100] + "..."
                })
                
    print(f"Near-duplicates identified: {len(near_dup_indices_to_remove)}")
    
    all_removed = exact_dup_indices_to_remove.union(near_dup_indices_to_remove)
    deduped_records = [r for idx, r in enumerate(records) if idx not in all_removed]
    
    print(f"Records retained after deduplication: {len(deduped_records)}")
    
    # Save deduplicated CSV
    with open(output_deduped_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped_records)
        
    # Generate Deduplication Report Markdown
    with open(report_md_path, mode="w", encoding="utf-8") as f:
        f.write("# OILPS Dataset Deduplication Report\n\n")
        f.write("## 1. Summary Statistics\n\n")
        f.write(f"- **Total Input Records:** {total_records}\n")
        f.write(f"- **Exact Duplicates Removed:** {len(exact_dup_indices_to_remove)}\n")
        f.write(f"- **Near Duplicates Removed:** {len(near_dup_indices_to_remove)}\n")
        f.write(f"- **Total Records Removed:** {len(all_removed)}\n")
        f.write(f"- **Final Clean Records Retained:** {len(deduped_records)}\n")
        f.write(f"- **Deduplication Rate:** {round((len(all_removed)/max(total_records,1))*100, 2)}%\n\n")
        
        f.write("## 2. Leakage Prevention Rationale\n\n")
        f.write("Deduplication is vital in precursor NLP tasks because identical incident descriptions across different reporting cycles or sources can cause artificial data leakage between training, validation, and test splits.\n\n")
        
        f.write("## 3. Sample Exact Duplicate Log (Top 10)\n\n")
        if exact_dup_logs:
            f.write("| Primary Record | Removed Duplicate | Source | Reason |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            for item in exact_dup_logs[:10]:
                f.write(f"| `{item['primary_record_id']}` | `{item['duplicate_record_id']}` | {item['source']} | {item['reason']} |\n")
        else:
            f.write("No exact duplicates detected.\n")
            
        f.write("\n## 4. Sample Near-Duplicate Log (Top 10)\n\n")
        if near_dup_logs:
            f.write("| Primary Record | Removed Duplicate | Similarity | Sources |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            for item in near_dup_logs[:10]:
                f.write(f"| `{item['primary_record_id']}` | `{item['duplicate_record_id']}` | {item['similarity_score']} | {item['source_a']} / {item['source_b']} |\n")
        else:
            f.write("No near duplicates detected above 0.85 threshold.\n")
            
    print(f"Saved deduplication report to {report_md_path}")
    return len(deduped_records)

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    in_csv = base_dir / "ai-service" / "datasets" / "processed" / "oilps_unified_raw.csv"
    out_csv = base_dir / "ai-service" / "datasets" / "processed" / "oilps_unified_deduped.csv"
    rep_md = base_dir / "ai-service" / "datasets" / "quality" / "deduplication_report.md"
    
    if in_csv.exists():
        run_deduplication(in_csv, out_csv, rep_md)
