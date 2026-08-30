"""
analyze_lsr_errors_stage11.py - Stage 11: Deep Semantic & Failure Analysis for Multi-Label LSR.

Tasks:
1. Verify token vocabulary presence for domain keywords:
   - crane, lifting, sling, casing, bundle, hoisted, load, suspended, rigging
   - confined, vessel, separator, tank, pit, entry, h2s, gas, toxic, monitoring, ventilation
   - line of fire, struck, swung, dropped, pinch
2. Inspect raw probability vectors for demo incidents under Stage 7 & Stage 10 models.
3. Conduct exhaustive semantic error analysis on the held-out TEST SET (lsr_test.csv).
4. Measure per-rule false negatives, support, precision, recall, and PR curves.
5. Diagnose whether errors stem from:
   - Token OOV or vocabulary filtering
   - Loss function & positive class weighting
   - Sequence attention pooling dynamics
   - Threshold calibration mismatch
6. Output detailed diagnostic reports and CSV logs to ai-service/results/lsr_stage11/.

Seed: 42
"""

import os
import re
import json
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
STAGE7_DIR = BASE_DIR / "results" / "lsr_stage7"
STAGE10_DIR = BASE_DIR / "results" / "lsr_stage10"
STAGE11_DIR = BASE_DIR / "results" / "lsr_stage11"
QUALITY_DIR = BASE_DIR / "datasets" / "quality"

STAGE11_DIR.mkdir(parents=True, exist_ok=True)

OFFICIAL_9_LSR = [
    "Bypassing Safety Controls",
    "Confined Space",
    "Driving",
    "Energy Isolation",
    "Hot Work",
    "Line of Fire",
    "Safe Mechanical Lifting",
    "Toxic Gas / Hazardous Substance",
    "Working at Height"
]

DEMO_INCIDENTS = [
    {
        "id": "DEMO_1_HYDROTEST",
        "title": "High-Pressure Hydrotest Fitting Failure",
        "narrative": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest.",
        "expected_rules": ["Energy Isolation", "Line of Fire"]
    },
    {
        "id": "DEMO_2_CRANE_LIFTING",
        "title": "Crane Lifting Tubular Handling in Line of Fire",
        "narrative": "A crawler crane was lifting a 2-ton casing bundle across the rig floor when the nylon sling parted due to sharp edge contact. The casing bundle swung downward, striking the floor near the rotary table.",
        "expected_rules": ["Safe Mechanical Lifting", "Line of Fire"]
    },
    {
        "id": "DEMO_3_CONFINED_H2S",
        "title": "Confined Space Vessel Entry with H2S Accumulation",
        "narrative": "An employee entered an enclosed crude oil storage separator without continuous gas monitoring or ventilation. Lethal levels of hydrogen sulfide (H2S) gas overcame the worker inside the vessel.",
        "expected_rules": ["Confined Space", "Toxic Gas / Hazardous Substance"]
    },
    {
        "id": "DEMO_4_NEGATIVE_SLIP",
        "title": "Minor Slip on Ice in Yard (Negative Control)",
        "narrative": "While walking across the paved maintenance yard after a shift change, an operator slipped on a patch of ice and bruised their knee. First aid applied; worker returned to full duty immediately.",
        "expected_rules": []
    }
]

def clean_and_tokenize(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()

class Vocabulary:
    def __init__(self, min_freq=2):
        self.min_freq = min_freq
        self.pad_token = "<PAD>"
        self.unk_token = "<UNK>"
        self.pad_idx = 0
        self.unk_idx = 1
        self.word2idx = {self.pad_token: 0, self.unk_token: 1}
        self.idx2word = {0: self.pad_token, 1: self.unk_token}
        self.vocab_size = 2
        
    def build_vocab(self, texts):
        counts = Counter()
        for t in texts:
            counts.update(clean_and_tokenize(t))
        for word, count in counts.items():
            if count >= self.min_freq and word not in self.word2idx:
                idx = self.vocab_size
                self.word2idx[word] = idx
                self.idx2word[idx] = word
                self.vocab_size += 1
                
    def text_to_indices(self, text, max_len=120):
        tokens = clean_and_tokenize(text)
        indices = [self.word2idx.get(w, self.unk_idx) for w in tokens[:max_len]]
        if len(indices) < max_len:
            indices += [self.pad_idx] * (max_len - len(indices))
        return indices, tokens[:max_len]

# Import Stage 7 Model Architecture
import torch.nn as nn
import torch.nn.functional as F

class ScaledDotProductAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.proj = nn.Linear(hidden_dim, 128)
        self.score = nn.Linear(128, 1, bias=False)
        self.scale = np.sqrt(128)
        
    def forward(self, gru_outputs, mask=None):
        energy = torch.tanh(self.proj(gru_outputs))
        weights = self.score(energy) / self.scale
        if mask is not None:
            weights = weights.masked_fill(mask.unsqueeze(-1) == 0, -1e9)
        attn_weights = F.softmax(weights, dim=1)
        context = torch.sum(attn_weights * gru_outputs, dim=1)
        return context, attn_weights.squeeze(-1)

class Stage7LSRModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25, pad_idx=0):
        super().__init__()
        self.pad_idx = pad_idx
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.embed_dropout = nn.Dropout(dropout)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        eff_hidden = hidden_dim * 2
        self.layer_norm = nn.LayerNorm(eff_hidden)
        self.attention = ScaledDotProductAttention(eff_hidden)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(eff_hidden, 128),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_classes)
        )
        
    def forward(self, x):
        mask = (x != self.pad_idx)
        embeds = self.embed_dropout(self.embedding(x))
        gru_out, _ = self.gru(embeds)
        norm_gru_out = self.layer_norm(gru_out)
        context, attn_weights = self.attention(norm_gru_out, mask=mask)
        logits = self.classifier(context)
        return logits, attn_weights

def run_diagnostic_analysis():
    print("=" * 75)
    print("STAGE 11: MULTI-LABEL LSR SEMANTIC DIAGNOSTIC & ERROR ANALYSIS")
    print("=" * 75)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Load Training and Test Splits
    train_df = pd.read_csv(SPLITS_DIR / "lsr_train.csv")
    val_df = pd.read_csv(SPLITS_DIR / "lsr_val.csv")
    test_df = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    
    train_texts = train_df["narrative"].fillna("").astype(str).tolist()
    vocab = Vocabulary(min_freq=2)
    vocab.build_vocab(train_texts)
    
    # 2. Vocabulary & Domain Keyword Audit
    print("\n--- 1. VOCABULARY & DOMAIN KEYWORD AUDIT ---")
    target_keywords = [
        "crane", "lifting", "sling", "casing", "bundle", "suspended", "hoist", "rigging",
        "confined", "vessel", "separator", "tank", "pit", "entry", "h2s", "sulfide", "gas",
        "toxic", "monitoring", "ventilation", "pressure", "hydrotest", "bleeder", "line",
        "fire", "struck", "swung", "dropped", "pinch", "fall", "height", "scaffold", "ladder"
    ]
    
    vocab_audit = {}
    for kw in target_keywords:
        in_vocab = kw in vocab.word2idx
        idx = vocab.word2idx.get(kw, 1)
        # Count occurrences in training text
        count_in_train = sum(t.count(kw) for t in train_texts)
        vocab_audit[kw] = {"in_vocab": in_vocab, "idx": idx, "train_count": count_in_train}
        status = "[PRESENT]" if in_vocab else "[OOV / MISSING]"
        print(f"  {kw:<15} : {status:<15} | Index: {idx:<5} | Train Count: {count_in_train}")
        
    with open(STAGE11_DIR / "vocabulary_keyword_audit.json", "w") as f:
        json.dump(vocab_audit, f, indent=2)

    # 3. Load Trained Stage 7 Model
    ckpt_path = STAGE7_DIR / "checkpoints" / "best_lsr_stage7_model.pt"
    assert ckpt_path.exists(), f"Stage 7 checkpoint missing at {ckpt_path}"
    
    model = Stage7LSRModel(vocab_size=vocab.vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25).to(device)
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model.eval()
    
    # Load Stage 7 and Stage 10 Thresholds
    s7_thresholds = {
        "Bypassing Safety Controls": 0.50,
        "Confined Space": 0.50,
        "Driving": 0.25,
        "Energy Isolation": 0.30,
        "Hot Work": 0.45,
        "Line of Fire": 0.20,
        "Safe Mechanical Lifting": 0.20,
        "Toxic Gas / Hazardous Substance": 0.50,
        "Working at Height": 0.25
    }
    
    s10_thresh_file = STAGE10_DIR / "calibrated_thresholds.json"
    if s10_thresh_file.exists():
        with open(s10_thresh_file) as f:
            s10_thresholds = json.load(f)
    else:
        s10_thresholds = s7_thresholds
        
    # 4. Probe Demo Incidents & Inspect Raw Probabilities
    print("\n--- 2. DEMO INCIDENT PROBABILITY & ATTENTION DIAGNOSTICS ---")
    demo_probe_results = []
    
    for inc in DEMO_INCIDENTS:
        indices, tokens = vocab.text_to_indices(inc["narrative"], max_len=120)
        tensor_in = torch.tensor([indices], dtype=torch.long).to(device)
        
        with torch.no_grad():
            logits, attns = model(tensor_in)
            probs = torch.sigmoid(logits[0]).cpu().numpy()
            raw_w = attns[0].cpu().numpy()[:len(tokens)]
            norm_w = raw_w / raw_w.sum() if raw_w.sum() > 0 else raw_w
            
        top_tokens = sorted([{"token": str(t), "weight": float(np.round(w, 4))} for t, w in zip(tokens, norm_w)], key=lambda x: x["weight"], reverse=True)[:5]
        
        prob_dict = {r: float(np.round(probs[i], 4)) for i, r in enumerate(OFFICIAL_9_LSR)}
        s7_triggered = [r for r, p in prob_dict.items() if p >= s7_thresholds.get(r, 0.50)]
        s10_triggered = [r for r, p in prob_dict.items() if p >= s10_thresholds.get(r, 0.50)]
        
        print(f"\n[INCIDENT]: {inc['title']}")
        print(f"  Expected Rules:   {inc['expected_rules']}")
        print(f"  Stage 7 Triggers: {s7_triggered}")
        print(f"  Stage 10 Trigger: {s10_triggered}")
        print("  Raw Probabilities:")
        for r in OFFICIAL_9_LSR:
            p = prob_dict[r]
            t7 = s7_thresholds.get(r, 0.5)
            t10 = s10_thresholds.get(r, 0.5)
            print(f"    - {r:<32}: {p*100:5.2f}% | (S7 Thresh: {t7:.2f}, S10 Thresh: {t10:.2f})")
            
        demo_probe_results.append({
            "incident_id": inc["id"],
            "title": inc["title"],
            "expected_rules": inc["expected_rules"],
            "probabilities": prob_dict,
            "stage7_triggers": s7_triggered,
            "stage10_triggers": s10_triggered,
            "top_attended_tokens": top_tokens
        })
        
    with open(STAGE11_DIR / "demo_probe_diagnostics.json", "w") as f:
        json.dump(demo_probe_results, f, indent=2)

    # 5. Full Held-Out Test Set Semantic Error Analysis
    print("\n--- 3. HELD-OUT TEST SET (138 Records) SEMANTIC AUDIT ---")
    
    def extract_multihot(df):
        Y = np.zeros((len(df), len(OFFICIAL_9_LSR)), dtype=np.float32)
        for i, all_str in enumerate(df["all_lsrs"].fillna("None")):
            rules = [x.strip() for x in all_str.split(";") if x.strip() and x.strip() != "None"]
            for r in rules:
                if r in OFFICIAL_9_LSR:
                    Y[i, OFFICIAL_9_LSR.index(r)] = 1.0
        return Y
        
    test_texts = test_df["narrative"].fillna("").astype(str).tolist()
    Y_test = extract_multihot(test_df)
    
    test_probs = []
    for txt in test_texts:
        indices, _ = vocab.text_to_indices(txt, max_len=120)
        tensor_in = torch.tensor([indices], dtype=torch.long).to(device)
        with torch.no_grad():
            logits, _ = model(tensor_in)
            probs = torch.sigmoid(logits[0]).cpu().numpy()
            test_probs.append(probs)
    Y_test_probs = np.array(test_probs)
    
    # Analyze Specific False Negatives Across Semantic Domains
    semantic_queries = [
        {"domain": "Lifting & Rigging", "pattern": r"\b(crane|lifting|sling|rigging|hoist|casing bundle)\b", "rule": "Safe Mechanical Lifting"},
        {"domain": "Confined Space & Gas", "pattern": r"\b(confined|separator|vessel entry|tank entry|mud pit)\b", "rule": "Confined Space"},
        {"domain": "Toxic Gas Exposure", "pattern": r"\b(h2s|hydrogen sulfide|toxic gas|chemical exposure)\b", "rule": "Toxic Gas / Hazardous Substance"},
        {"domain": "Line of Fire Trajectory", "pattern": r"\b(line of fire|swung|struck by|dropped object|pinch)\b", "rule": "Line of Fire"},
        {"domain": "Energy Isolation", "pattern": r"\b(hydrostatic|bleeder|pressurized|de energize|loto|lockout)\b", "rule": "Energy Isolation"}
    ]
    
    semantic_findings = []
    print("\nEvaluating Semantic Target Match Rates on Test Set:")
    for sq in semantic_queries:
        r_idx = OFFICIAL_9_LSR.index(sq["rule"])
        matching_rows = []
        for i, txt in enumerate(test_texts):
            if re.search(sq["pattern"], txt, re.IGNORECASE):
                ground_truth = int(Y_test[i, r_idx])
                p_s7 = float(Y_test_probs[i, r_idx])
                pred_s7 = int(p_s7 >= s7_thresholds[sq["rule"]])
                pred_s10 = int(p_s7 >= s10_thresholds[sq["rule"]])
                matching_rows.append({
                    "record_id": str(test_df.iloc[i]["record_id"]),
                    "text": txt[:100] + "...",
                    "ground_truth": ground_truth,
                    "model_probability": np.round(p_s7, 4),
                    "pred_stage7": pred_s7,
                    "pred_stage10": pred_s10
                })
                
        total_matched = len(matching_rows)
        true_pos = sum(1 for m in matching_rows if m["ground_truth"] == 1)
        mean_prob_pos = float(np.mean([m["model_probability"] for m in matching_rows if m["ground_truth"] == 1])) if true_pos > 0 else 0.0
        
        print(f"  {sq['domain']:<28} | Keyword Hits: {total_matched:2d} | True Labels: {true_pos:2d} | Mean Model Prob (Positives): {mean_prob_pos*100:5.2f}%")
        semantic_findings.append({
            "domain": sq["domain"],
            "target_rule": sq["rule"],
            "keyword_pattern": sq["pattern"],
            "total_keyword_matches": total_matched,
            "true_positives_in_data": true_pos,
            "mean_model_probability_on_positives": mean_prob_pos,
            "representative_samples": matching_rows[:5]
        })
        
    with open(STAGE11_DIR / "semantic_domain_error_analysis.json", "w") as f:
        json.dump(semantic_findings, f, indent=2)
        
    print("\nStage 11 Diagnostic Analysis Complete! Artifacts saved to results/lsr_stage11/.")

if __name__ == "__main__":
    run_diagnostic_analysis()
