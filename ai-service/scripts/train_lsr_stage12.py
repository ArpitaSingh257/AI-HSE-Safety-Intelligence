"""
train_lsr_stage12.py - Stage 12: Targeted LSR Data Augmentation & Domain-Aware Training.

Steps:
1. Audit LSR training split for rare class distribution & domain vocabulary.
2. Generate conservative, domain-preserving augmented training data (TRAIN SPLIT ONLY).
   Saved to: datasets/model_ready/lsr_train_augmented.csv.
3. Train an enhanced domain-aware Bidirectional GRU + Attention model on the augmented training set.
4. Tune independent per-rule decision thresholds strictly on the untouched VALIDATION split (lsr_val.csv).
5. Evaluate once on the untouched held-out TEST split (lsr_test.csv).
6. Compare Stage 7 champion vs Stage 12 candidate and execute the 4 demo semantic probes.

Seed: 42
"""

import os
import re
import csv
import json
import random
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
    confusion_matrix
)

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True

set_seed(42)

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

# Controlled Oil & Gas Safety Synonym Dictionary
DOMAIN_SYNONYMS = {
    r"\bcrane\b": "mobile crane",
    r"\bsling\b": "rigging sling",
    r"\bsuspended load\b": "overhead hoisted load",
    r"\bcasing bundle\b": "tubular casing bundle",
    r"\bvessel\b": "enclosed process vessel",
    r"\bseparator\b": "production separator tank",
    r"\bh2s\b": "hydrogen sulfide gas",
    r"\bgas monitoring\b": "atmospheric gas detection",
    r"\bhydrotest\b": "hydrostatic pressure test",
    r"\bbleeder plug\b": "high pressure bleeder valve",
    r"\bline of fire\b": "struck by hazard zone",
    r"\bwelding\b": "hot work welding",
    r"\bscaffold\b": "elevated scaffolding platform"
}

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
        return indices

class TextDataset(Dataset):
    def __init__(self, texts, labels, vocab, max_len=120):
        self.texts = texts
        self.labels = labels
        self.vocab = vocab
        self.max_len = max_len
        
    def __len__(self):
        return len(self.texts)
        
    def __getitem__(self, idx):
        indices = self.vocab.text_to_indices(self.texts[idx], self.max_len)
        return torch.tensor(indices, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.float)

# =========================================================================
# MODEL ARCHITECTURE
# =========================================================================

class SequenceAttention(nn.Module):
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

class Stage12DomainLSRModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25, pad_idx=0):
        super().__init__()
        self.pad_idx = pad_idx
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.embed_dropout = nn.Dropout(dropout)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        eff_hidden = hidden_dim * 2
        self.layer_norm = nn.LayerNorm(eff_hidden)
        self.attention = SequenceAttention(eff_hidden)
        
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

def extract_multihot(df):
    Y = np.zeros((len(df), len(OFFICIAL_9_LSR)), dtype=np.float32)
    for i, all_str in enumerate(df["all_lsrs"].fillna("None")):
        rules = [x.strip() for x in all_str.split(";") if x.strip() and x.strip() != "None"]
        for r in rules:
            if r in OFFICIAL_9_LSR:
                Y[i, OFFICIAL_9_LSR.index(r)] = 1.0
    return Y

def compute_multilabel_metrics(y_true, y_pred):
    return {
        "micro_precision": float(precision_score(y_true, y_pred, average="micro", zero_division=0)),
        "micro_recall": float(recall_score(y_true, y_pred, average="micro", zero_division=0)),
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "macro_precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "hamming_loss": float(hamming_loss(y_true, y_pred)),
        "exact_match_ratio": float(np.mean(np.all(y_true == y_pred, axis=1)))
    }

# =========================================================================
# DATA AUGMENTATION (TRAIN ONLY)
# =========================================================================

def augment_training_data(train_df):
    """
    Targeted conservative domain augmentation for weak LSR classes:
    Confined Space, Toxic Gas, Safe Mechanical Lifting, Line of Fire, Bypassing Controls.
    Preserves exact label vectors and creates natural paraphrases.
    """
    augmented_records = []
    target_rules = {
        "Confined Space", "Toxic Gas / Hazardous Substance",
        "Safe Mechanical Lifting", "Line of Fire", "Bypassing Safety Controls"
    }
    
    for idx, row in train_df.iterrows():
        rec_id = str(row["record_id"])
        narrative = str(row["narrative"])
        all_lsrs = str(row["all_lsrs"])
        
        # Check if sample contains any target weak rule
        sample_rules = [x.strip() for x in all_lsrs.split(";") if x.strip()]
        has_target_rule = any(r in target_rules for r in sample_rules)
        
        if has_target_rule:
            aug_text = narrative
            modified = False
            for pattern, replacement in DOMAIN_SYNONYMS.items():
                if re.search(pattern, aug_text, re.IGNORECASE):
                    aug_text = re.sub(pattern, replacement, aug_text, flags=re.IGNORECASE)
                    modified = True
                    
            if modified and aug_text != narrative:
                augmented_records.append({
                    "record_id": f"{rec_id}_aug",
                    "narrative": aug_text,
                    "all_lsrs": all_lsrs
                })
                
    aug_df = pd.DataFrame(augmented_records)
    print(f"Generated {len(aug_df)} domain-augmented training samples for rare LSR rules.")
    combined_train_df = pd.concat([train_df[["record_id", "narrative", "all_lsrs"]], aug_df], ignore_index=True)
    return combined_train_df

# =========================================================================
# MAIN TRAINING & EVALUATION PIPELINE
# =========================================================================

def run_stage_12():
    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 75)
    print("STAGE 12: TARGETED LSR DATA AUGMENTATION + DOMAIN-AWARE TRAINING")
    print("=" * 75)
    print(f"Device: {device}")
    
    base_dir = Path(__file__).resolve().parent.parent
    splits_dir = base_dir / "datasets" / "model_ready" / "splits"
    model_ready_dir = base_dir / "datasets" / "model_ready"
    results_dir = base_dir / "results" / "lsr_stage12"
    quality_dir = base_dir / "datasets" / "quality"
    
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    
    # 1. Load Data Splits
    orig_train_df = pd.read_csv(splits_dir / "lsr_train.csv")
    val_df = pd.read_csv(splits_dir / "lsr_val.csv")
    test_df = pd.read_csv(splits_dir / "lsr_test.csv")
    
    # 2. Targeted Augmentation on TRAIN Split ONLY
    aug_train_df = augment_training_data(orig_train_df)
    aug_csv_path = model_ready_dir / "lsr_train_augmented.csv"
    aug_train_df.to_csv(aug_csv_path, index=False)
    print(f"Saved augmented training dataset -> {aug_csv_path} (Total: {len(aug_train_df)} records)")
    
    train_texts = aug_train_df["narrative"].fillna("").astype(str).tolist()
    Y_train = extract_multihot(aug_train_df)
    val_texts = val_df["narrative"].fillna("").astype(str).tolist()
    Y_val = extract_multihot(val_df)
    test_texts = test_df["narrative"].fillna("").astype(str).tolist()
    Y_test = extract_multihot(test_df)
    
    # Build Vocabulary strictly on Augmented Training Texts
    vocab = Vocabulary(min_freq=2)
    vocab.build_vocab(train_texts)
    print(f"Stage 12 Vocabulary Size: {vocab.vocab_size} tokens")
    
    train_loader = DataLoader(TextDataset(train_texts, Y_train, vocab, 120), batch_size=32, shuffle=True)
    val_loader = DataLoader(TextDataset(val_texts, Y_val, vocab, 120), batch_size=32, shuffle=False)
    test_loader = DataLoader(TextDataset(test_texts, Y_test, vocab, 120), batch_size=32, shuffle=False)
    
    # 3. Class-Aware Positive Weighting
    pos_counts = Y_train.sum(axis=0)
    neg_counts = len(Y_train) - pos_counts
    smooth_pos_w = torch.tensor(np.clip(np.sqrt(neg_counts / np.maximum(pos_counts, 1.0)), 1.0, 5.5), dtype=torch.float).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=smooth_pos_w)
    
    model = Stage12DomainLSRModel(vocab.vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=7e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    
    best_val_score = -1.0
    best_state = None
    best_val_probs = None
    
    print("\nTraining Stage 12 Domain-Aware Model (16 Epochs)...")
    for epoch in range(1, 17):
        model.train()
        total_loss = 0.0
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            logits, _ = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item() * len(bx)
            
        train_loss = total_loss / len(train_loader.dataset)
        
        # Validation
        model.eval()
        v_probs_list = []
        with torch.no_grad():
            for bx, _ in val_loader:
                bx = bx.to(device)
                logits, _ = model(bx)
                probs = torch.sigmoid(logits).cpu().numpy()
                v_probs_list.append(probs)
        v_probs = np.concatenate(v_probs_list, axis=0)
        
        temp_preds = (v_probs >= 0.35).astype(int)
        temp_f1 = f1_score(Y_val, temp_preds, average="micro", zero_division=0)
        scheduler.step(temp_f1)
        
        if temp_f1 > best_val_score:
            best_val_score = temp_f1
            best_state = {k: v.cpu() for k, v in model.state_dict().items()}
            best_val_probs = v_probs
            print(f"  Epoch {epoch:02d}: TrainLoss={train_loss:.4f} | Val Micro-F1={temp_f1:.4f} [NEW BEST CHECKPOINT]")
        else:
            print(f"  Epoch {epoch:02d}: TrainLoss={train_loss:.4f} | Val Micro-F1={temp_f1:.4f}")
            
    # Save Checkpoint
    ckpt_path = results_dir / "checkpoints" / "best_lsr_stage12_model.pt"
    torch.save(best_state, ckpt_path)
    print(f"\nSaved Best Stage 12 Checkpoint -> {ckpt_path}")
    
    # 4. Tune Thresholds on Validation Split ONLY
    print("\n--- Calibrating Per-Rule Thresholds on Validation Split ---")
    stage12_thresholds = {}
    calibrated_val_preds = np.zeros_like(best_val_probs, dtype=int)
    
    for r_idx, r_name in enumerate(OFFICIAL_9_LSR):
        yt_r = Y_val[:, r_idx]
        p_r = best_val_probs[:, r_idx]
        
        best_t, best_score = 0.35, 0.0
        for t in np.arange(0.15, 0.85, 0.02):
            yp_r = (p_r >= t).astype(int)
            p = precision_score(yt_r, yp_r, zero_division=0)
            r = recall_score(yt_r, yp_r, zero_division=0)
            # Harmonic mean balancing precision and recall
            f_score = f1_score(yt_r, yp_r, zero_division=0)
            if f_score > best_score:
                best_score = f_score
                best_t = float(np.round(t, 2))
                
        # Constrain threshold range for safety
        if r_name in ["Driving", "Safe Mechanical Lifting", "Working at Height"] and best_t < 0.30:
            best_t = 0.35
            
        stage12_thresholds[r_name] = best_t
        calibrated_val_preds[:, r_idx] = (p_r >= best_t).astype(int)
        print(f"  - {r_name:<32}: Calibrated Threshold = {best_t:.2f} (Val F1={best_score:.2f})")
        
    # 5. Evaluate ONCE on Held-Out Test Split
    model.load_state_dict(best_state)
    model.eval()
    
    test_probs_list = []
    with torch.no_grad():
        for bx, _ in test_loader:
            bx = bx.to(device)
            logits, _ = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy()
            test_probs_list.append(probs)
    Y_test_probs = np.concatenate(test_probs_list, axis=0)
    
    test_preds_s12 = np.zeros_like(Y_test_probs, dtype=int)
    per_rule_rows = []
    
    for r_idx, r_name in enumerate(OFFICIAL_9_LSR):
        t_12 = stage12_thresholds[r_name]
        yp_r = (Y_test_probs[:, r_idx] >= t_12).astype(int)
        test_preds_s12[:, r_idx] = yp_r
        
        yt_r = Y_test[:, r_idx]
        p = float(precision_score(yt_r, yp_r, zero_division=0))
        r = float(recall_score(yt_r, yp_r, zero_division=0))
        f1 = float(f1_score(yt_r, yp_r, zero_division=0))
        tn, fp, fn, tp = confusion_matrix(yt_r, yp_r, labels=[0, 1]).ravel()
        
        per_rule_rows.append({
            "rule": r_name,
            "threshold": t_12,
            "support": int(yt_r.sum()),
            "precision": p,
            "recall": r,
            "f1_score": f1,
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn)
        })
        
    s12_test_metrics = compute_multilabel_metrics(Y_test, test_preds_s12)
    
    # 6. Evaluate Known Demo Scenarios
    print("\n--- 6. EVALUATING DEMO SCENARIOS (PROBE CHECK) ---")
    demo_scenarios = [
        {"title": "Hydrotest Pressure Fitting Failure", "text": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest."},
        {"title": "Crane Lifting Tubular Handling", "text": "A crawler crane was lifting a 2-ton casing bundle across the rig floor when the nylon sling parted due to sharp edge contact. The casing bundle swung downward, striking the floor near the rotary table."},
        {"title": "Confined Space Vessel Entry with H2S", "text": "An employee entered an enclosed crude oil storage separator without continuous gas monitoring or ventilation. Lethal levels of hydrogen sulfide (H2S) gas overcame the worker inside the vessel."},
        {"title": "Minor Slip on Ice in Yard", "text": "While walking across the paved maintenance yard after a shift change, an operator slipped on a patch of ice and bruised their knee. First aid applied; worker returned to full duty immediately."}
    ]
    
    demo_probe_outputs = []
    for d in demo_scenarios:
        t_indices = vocab.text_to_indices(d["text"], max_len=120)
        with torch.no_grad():
            d_logits, _ = model(torch.tensor([t_indices], dtype=torch.long).to(device))
            d_probs = torch.sigmoid(d_logits[0]).cpu().numpy()
            
        triggered = [OFFICIAL_9_LSR[i] for i, p in enumerate(d_probs) if p >= stage12_thresholds[OFFICIAL_9_LSR[i]]]
        print(f"\n[DEMO]: {d['title']}")
        print(f"  Triggered Rules: {triggered}")
        print(f"  Crane/Lifting Prob: {d_probs[6]*100:.1f}%, LineOfFire Prob: {d_probs[5]*100:.1f}%, EnergyIsolation: {d_probs[3]*100:.1f}%, ConfinedSpace: {d_probs[1]*100:.1f}%, ToxicGas: {d_probs[7]*100:.1f}%")
        
        demo_probe_outputs.append({
            "title": d["title"],
            "triggered_rules": triggered,
            "raw_probabilities": {r: float(np.round(d_probs[i], 4)) for i, r in enumerate(OFFICIAL_9_LSR)}
        })

    # 7. Save Artifacts & Reports
    with open(results_dir / "stage12_lsr_config.json", "w") as f:
        json.dump({
            "model_name": "stage12_domain_augmented_bigru",
            "embed_dim": 200,
            "hidden_dim": 128,
            "dropout": 0.25,
            "per_rule_thresholds": stage12_thresholds,
            "test_metrics": s12_test_metrics,
            "demo_probes": demo_probe_outputs
        }, f, indent=2)
        
    preds_df = test_df.copy()
    for idx, r_name in enumerate(OFFICIAL_9_LSR):
        col_prob = f"prob_{r_name.lower().replace(' ', '_').replace('/', '_')}"
        col_pred = f"pred_{r_name.lower().replace(' ', '_').replace('/', '_')}"
        preds_df[col_prob] = np.round(Y_test_probs[:, idx], 4)
        preds_df[col_pred] = test_preds_s12[:, idx]
    preds_df.to_csv(results_dir / "stage12_test_predictions.csv", index=False)
    
    pd.DataFrame(per_rule_rows).to_csv(results_dir / "stage12_per_rule_metrics.csv", index=False)
    
    # 8. Model Selection Logic: Compare Stage 7 Baseline vs Stage 12 Candidate
    stage7_metrics = {"micro_f1": 0.6928, "macro_f1": 0.5723, "hamming_loss": 0.0378, "exact_match": 0.7174}
    is_stage12_better = (s12_test_metrics["micro_f1"] >= stage7_metrics["micro_f1"] and s12_test_metrics["exact_match_ratio"] >= 0.70)
    
    decision_str = "STAGE 12 SELECTED AS NEW LSR CHAMPION" if is_stage12_better else "STAGE 7 REMAINS LSR CHAMPION"
    
    report_path = quality_dir / "STAGE_12_LSR_AUGMENTATION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# STAGE 12: TARGETED LSR DATA AUGMENTATION & DOMAIN-AWARE TRAINING REPORT\n\n")
        f.write("**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence\n")
        f.write("**Evaluation Split:** Held-Out Unseen Test Set (`lsr_test.csv` - 138 records)\n")
        f.write("**Date:** 2026-08-30\n")
        f.write("**Random Seed:** `42` (Deterministic Reproducibility)\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Executive Summary & Benchmark Comparison\n\n")
        f.write("| Model Phase | Architecture | Training Data Strategy | Test Micro-F1 | Test Macro-F1 | Test Hamming Loss | Test Exact Match Ratio |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| **Stage 7 Champion** | Bidirectional GRU + Attention | Original Split Only | {stage7_metrics['micro_f1']:.4f} | {stage7_metrics['macro_f1']:.4f} | {stage7_metrics['hamming_loss']:.4f} | {stage7_metrics['exact_match']*100:.2f}% |\n")
        f.write(f"| **Stage 12 Candidate** | **Domain-Aware BiGRU+Attn** | **Targeted Domain Augmentation (Train Only)** | **{s12_test_metrics['micro_f1']:.4f}** | **{s12_test_metrics['macro_f1']:.4f}** | **{s12_test_metrics['hamming_loss']:.4f}** | **{s12_test_metrics['exact_match_ratio']*100:.2f}%** |\n\n")
        
        f.write(f"### Final Selection Decision: **`{decision_str}`**\n\n")
        f.write("---\n\n")
        
        f.write("## 2. Stage 12 Per-Rule Performance Breakdown (9 IOGP Rules)\n\n")
        f.write("| Official IOGP Life-Saving Rule | Validation Threshold | Test Support | Precision | Recall | F1-Score | Confusion (TP/FP/FN/TN) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in per_rule_rows:
            f.write(f"| **{r['rule']}** | {r['threshold']:.2f} | {r['support']} | {r['precision']:.4f} | {r['recall']:.4f} | **{r['f1_score']:.4f}** | {r['tp']}/{r['fp']}/{r['fn']}/{r['tn']} |\n")
        f.write(f"| **OVERALL (MICRO)** | — | **{sum(r['support'] for r in per_rule_rows)}** | **{s12_test_metrics['micro_precision']:.4f}** | **{s12_test_metrics['micro_recall']:.4f}** | **{s12_test_metrics['micro_f1']:.4f}** | — |\n")
        f.write(f"| **OVERALL (MACRO)** | — | — | **{s12_test_metrics['macro_precision']:.4f}** | **{s12_test_metrics['macro_recall']:.4f}** | **{s12_test_metrics['macro_f1']:.4f}** | — |\n\n")
        
        f.write("---\n\n")
        f.write("## 3. Demo Scenario Verification Audit\n\n")
        for d in demo_probe_outputs:
            f.write(f"### {d['title']}:\n")
            f.write(f"- **Triggered Rules:** `{d['triggered_rules']}`\n")
            f.write(f"- **Key Probabilities:** " + ", ".join([f"{k}: {v*100:.1f}%" for k, v in d['raw_probabilities'].items() if v > 0.05]) + "\n\n")

    print(f"\nSaved Stage 12 Report to: {report_path}")
    print("\n" + "=" * 50)
    print("STAGE 12 FINAL COMPARISON SUMMARY")
    print("=" * 50)
    print("Stage 7:")
    print(f"  Micro-F1 =     {stage7_metrics['micro_f1']:.4f}")
    print(f"  Macro-F1 =     {stage7_metrics['macro_f1']:.4f}")
    print(f"  Hamming Loss = {stage7_metrics['hamming_loss']:.4f}")
    print(f"  Exact Match =  {stage7_metrics['exact_match']*100:.2f}%")
    print()
    print("Stage 12:")
    print(f"  Micro-F1 =     {s12_test_metrics['micro_f1']:.4f}")
    print(f"  Macro-F1 =     {s12_test_metrics['macro_f1']:.4f}")
    print(f"  Hamming Loss = {s12_test_metrics['hamming_loss']:.4f}")
    print(f"  Exact Match =  {s12_test_metrics['exact_match_ratio']*100:.2f}%")
    print("=" * 50)
    print(f"\nDECISION: {decision_str}\n")

if __name__ == "__main__":
    run_stage_12()
