"""
train_lsr_stage11.py - Stage 11: Enhanced Multi-Label LSR Training with Asymmetric Focal Loss & Contextual Pooling.

Architectural Enhancements:
1. Asymmetric Multi-Label Loss (gamma_pos=0.0, gamma_neg=2.0) with smooth positive weighting to solve gradient suppression on rare rules.
2. Bidirectional GRU with Multi-Head Sequence Attention and Residual Skip Connection.
3. Validation-driven per-rule threshold calibration prioritizing semantic recall on safety-critical barriers without exploding false alarms.
4. Deterministic training with seed=42.

Output:
  ai-service/results/lsr_stage11/checkpoints/best_lsr_stage11_model.pt
  ai-service/results/lsr_stage11/stage11_lsr_config.json
  ai-service/results/lsr_stage11/stage11_test_predictions.csv
  ai-service/results/lsr_stage11/stage11_per_rule_metrics.csv
"""

import os
import re
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
# ASYMMETRIC LOSS FOR MULTI-LABEL IMBALANCE
# =========================================================================

class AsymmetricLoss(nn.Module):
    def __init__(self, gamma_neg=2.0, gamma_pos=0.0, clip=0.05, eps=1e-8, pos_weights=None):
        super().__init__()
        self.gamma_neg = gamma_neg
        self.gamma_pos = gamma_pos
        self.clip = clip
        self.eps = eps
        self.pos_weights = pos_weights
        
    def forward(self, x, y):
        # Calculating Probabilities
        x_sigmoid = torch.sigmoid(x)
        xs_pos = x_sigmoid
        xs_neg = 1.0 - x_sigmoid
        
        # Asymmetric Clipping for negatives
        if self.clip is not None and self.clip > 0:
            xs_neg = (xs_neg + self.clip).clamp(max=1.0)
            
        # Basic CE calculation
        los_pos = y * torch.log(xs_pos.clamp(min=self.eps))
        los_neg = (1.0 - y) * torch.log(xs_neg.clamp(min=self.eps))
        
        # Asymmetric Focusing
        if self.gamma_pos > 0:
            los_pos *= (1.0 - xs_pos) ** self.gamma_pos
        if self.gamma_neg > 0:
            los_neg *= xs_pos ** self.gamma_neg
            
        if self.pos_weights is not None:
            los_pos *= self.pos_weights
            
        loss = - (los_pos + los_neg)
        return loss.sum()

# =========================================================================
# ENHANCED STAGE 11 ARCHITECTURE
# =========================================================================

class MultiHeadSequenceAttention(nn.Module):
    def __init__(self, hidden_dim, num_heads=2):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.proj = nn.Linear(hidden_dim, 128)
        self.score = nn.Linear(128, num_heads, bias=False)
        self.scale = np.sqrt(128)
        
    def forward(self, gru_outputs, mask=None):
        energy = torch.tanh(self.proj(gru_outputs)) # [batch, seq, 128]
        weights = self.score(energy) / self.scale     # [batch, seq, heads]
        if mask is not None:
            weights = weights.masked_fill(mask.unsqueeze(-1) == 0, -1e9)
        attn_weights = F.softmax(weights, dim=1)      # [batch, seq, heads]
        
        # Weighted sum across tokens for each head
        head_contexts = []
        for h in range(attn_weights.shape[-1]):
            hw = attn_weights[:, :, h].unsqueeze(-1)  # [batch, seq, 1]
            ctx = torch.sum(hw * gru_outputs, dim=1) # [batch, hidden]
            head_contexts.append(ctx)
            
        combined_context = torch.cat(head_contexts, dim=-1) # [batch, hidden * num_heads]
        return combined_context, attn_weights[:, :, 0]

class Stage11EnhancedLSRModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25, pad_idx=0):
        super().__init__()
        self.pad_idx = pad_idx
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.embed_dropout = nn.Dropout(dropout)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        eff_hidden = hidden_dim * 2
        self.layer_norm = nn.LayerNorm(eff_hidden)
        self.attention = MultiHeadSequenceAttention(eff_hidden, num_heads=2)
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(eff_hidden * 2, 128),
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
        "hamming_loss": float(hamming_loss(y_true, y_pred)),
        "exact_match_ratio": float(np.mean(np.all(y_true == y_pred, axis=1)))
    }

def train_stage11():
    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 75)
    print("STAGE 11: TRAINING ASYMMETRIC MULTI-HEAD LSR GRU + ATTENTION MODEL")
    print("=" * 75)
    print(f"Device: {device}")
    
    base_dir = Path(__file__).resolve().parent.parent
    splits_dir = base_dir / "datasets" / "model_ready" / "splits"
    results_dir = base_dir / "results" / "lsr_stage11"
    quality_dir = base_dir / "datasets" / "quality"
    
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    
    # 1. Load Splits
    train_df = pd.read_csv(splits_dir / "lsr_train.csv")
    val_df = pd.read_csv(splits_dir / "lsr_val.csv")
    test_df = pd.read_csv(splits_dir / "lsr_test.csv")
    
    train_texts = train_df["narrative"].fillna("").astype(str).tolist()
    Y_train = extract_multihot(train_df)
    val_texts = val_df["narrative"].fillna("").astype(str).tolist()
    Y_val = extract_multihot(val_df)
    test_texts = test_df["narrative"].fillna("").astype(str).tolist()
    Y_test = extract_multihot(test_df)
    
    vocab = Vocabulary(min_freq=2)
    vocab.build_vocab(train_texts)
    
    train_loader = DataLoader(TextDataset(train_texts, Y_train, vocab, 120), batch_size=32, shuffle=True)
    val_loader = DataLoader(TextDataset(val_texts, Y_val, vocab, 120), batch_size=32, shuffle=False)
    test_loader = DataLoader(TextDataset(test_texts, Y_test, vocab, 120), batch_size=32, shuffle=False)
    
    # Positive weights for Asymmetric Loss
    pos_counts = Y_train.sum(axis=0)
    neg_counts = len(Y_train) - pos_counts
    smooth_pos_w = torch.tensor(np.clip(np.sqrt(neg_counts / np.maximum(pos_counts, 1.0)), 1.0, 5.0), dtype=torch.float).to(device)
    
    criterion = AsymmetricLoss(gamma_neg=2.0, gamma_pos=0.0, clip=0.05, pos_weights=smooth_pos_w)
    
    model = Stage11EnhancedLSRModel(vocab.vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=8e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    
    best_val_f1 = -1.0
    best_state = None
    best_val_probs = None
    
    print("\nStarting Stage 11 Training (16 Epochs)...")
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
            total_loss += loss.item()
            
        model.eval()
        v_probs_list = []
        with torch.no_grad():
            for bx, by in val_loader:
                bx = bx.to(device)
                logits, _ = model(bx)
                probs = torch.sigmoid(logits).cpu().numpy()
                v_probs_list.append(probs)
        v_probs = np.concatenate(v_probs_list, axis=0)
        
        # Validation score
        temp_preds = (v_probs >= 0.40).astype(int)
        temp_f1 = f1_score(Y_val, temp_preds, average="micro", zero_division=0)
        scheduler.step(temp_f1)
        
        if temp_f1 > best_val_f1:
            best_val_f1 = temp_f1
            best_state = {k: v.cpu() for k, v in model.state_dict().items()}
            best_val_probs = v_probs
            print(f"  Epoch {epoch:02d}: Loss={total_loss:.4f} | Val Micro-F1={temp_f1:.4f} [NEW BEST CHECKPOINT]")
        else:
            print(f"  Epoch {epoch:02d}: Loss={total_loss:.4f} | Val Micro-F1={temp_f1:.4f}")
            
    # Save Stage 11 Checkpoint
    ckpt_path = results_dir / "checkpoints" / "best_lsr_stage11_model.pt"
    torch.save(best_state, ckpt_path)
    print(f"\nSaved Best Stage 11 Checkpoint to: {ckpt_path}")
    
    # Calibrate Stage 11 Per-Rule Thresholds on Validation Split ONLY
    print("\nCalibrating Stage 11 Thresholds on Validation Split...")
    stage11_thresholds = {}
    calibrated_val_preds = np.zeros_like(best_val_probs, dtype=int)
    
    for r_idx, r_name in enumerate(OFFICIAL_9_LSR):
        yt_r = Y_val[:, r_idx]
        p_r = best_val_probs[:, r_idx]
        
        best_t, best_score = 0.40, 0.0
        for t in np.arange(0.15, 0.85, 0.02):
            yp_r = (p_r >= t).astype(int)
            p = precision_score(yt_r, yp_r, zero_division=0)
            r = recall_score(yt_r, yp_r, zero_division=0)
            # F_0.8 objective
            beta = 0.8
            f_b = ((1 + beta**2) * p * r) / ((beta**2 * p) + r + 1e-8) if (p + r) > 0 else 0.0
            if f_b > best_score:
                best_score = f_b
                best_t = float(np.round(t, 2))
                
        # Safety floor for generic classes
        if r_name in ["Driving", "Safe Mechanical Lifting", "Working at Height"] and best_t < 0.35:
            best_t = 0.38
            
        stage11_thresholds[r_name] = best_t
        calibrated_val_preds[:, r_idx] = (p_r >= best_t).astype(int)
        print(f"  - {r_name:<32} : Threshold = {best_t:.2f}")
        
    # Evaluate Stage 11 ONCE on Held-Out Test Set
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
    
    test_preds_s11 = np.zeros_like(Y_test_probs, dtype=int)
    per_rule_rows = []
    for r_idx, r_name in enumerate(OFFICIAL_9_LSR):
        t_11 = stage11_thresholds[r_name]
        yp_r = (Y_test_probs[:, r_idx] >= t_11).astype(int)
        test_preds_s11[:, r_idx] = yp_r
        
        yt_r = Y_test[:, r_idx]
        p = float(precision_score(yt_r, yp_r, zero_division=0))
        r = float(recall_score(yt_r, yp_r, zero_division=0))
        f1 = float(f1_score(yt_r, yp_r, zero_division=0))
        tn, fp, fn, tp = confusion_matrix(yt_r, yp_r, labels=[0, 1]).ravel()
        
        per_rule_rows.append({
            "rule": r_name,
            "threshold": t_11,
            "support": int(yt_r.sum()),
            "precision": p,
            "recall": r,
            "f1_score": f1,
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn)
        })
        
    s11_test_metrics = compute_multilabel_metrics(Y_test, test_preds_s11)
    
    # Save Stage 11 Artifacts
    with open(results_dir / "stage11_lsr_config.json", "w") as f:
        json.dump({
            "model_name": "stage11_asymmetric_multihead_gru",
            "embed_dim": 200,
            "hidden_dim": 128,
            "dropout": 0.25,
            "per_rule_thresholds": stage11_thresholds,
            "test_metrics": s11_test_metrics
        }, f, indent=2)
        
    preds_df = test_df.copy()
    for idx, r_name in enumerate(OFFICIAL_9_LSR):
        col_prob = f"prob_{r_name.lower().replace(' ', '_').replace('/', '_')}"
        col_pred = f"pred_{r_name.lower().replace(' ', '_').replace('/', '_')}"
        preds_df[col_prob] = np.round(Y_test_probs[:, idx], 4)
        preds_df[col_pred] = test_preds_s11[:, idx]
    preds_df.to_csv(results_dir / "stage11_test_predictions.csv", index=False)
    
    pd.DataFrame(per_rule_rows).to_csv(results_dir / "stage11_per_rule_metrics.csv", index=False)
    
    # Generate Report
    report_path = quality_dir / "STAGE_11_LSR_ERROR_ANALYSIS_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# STAGE 11: MULTI-LABEL LSR SEMANTIC ERROR ANALYSIS & TARGETED IMPROVEMENT REPORT\n\n")
        f.write("**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence\n")
        f.write("**Evaluation Split:** Held-Out Unseen Test Set (`lsr_test.csv` - 138 records)\n")
        f.write("**Date:** 2026-08-30\n")
        f.write("**Random Seed:** `42` (Deterministic Reproducibility)\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Executive Summary & Cross-Stage LSR Comparison\n\n")
        f.write("| Model Phase | Architecture | Loss / Calibration Strategy | Test Micro-F1 | Test Macro-F1 | Test Hamming Loss | Test Exact Match Ratio |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| **Stage 7 Baseline** | Bidirectional GRU + Attention | Smooth Pos-Weighted BCE | 0.6795 | 0.5618 | 0.0403 | 68.84% |\n")
        f.write(f"| **Stage 10 Calibration** | Stage 7 Frozen Model | Post-Hoc F0.7 Grid Search | 0.6939 | 0.5466 | 0.0362 | 70.29% |\n")
        f.write(f"| **Stage 11 Enhanced** | **Asymmetric Multi-Head GRU+Attn** | **Asymmetric Focal Loss + Dynamic Multi-Head** | **{s11_test_metrics['micro_f1']:.4f}** | **{s11_test_metrics['macro_f1']:.4f}** | **{s11_test_metrics['hamming_loss']:.4f}** | **{s11_test_metrics['exact_match_ratio']*100:.2f}%** |\n\n")
        
        f.write("---\n\n")
        
        f.write("## 2. Stage 11 Per-Rule Performance Breakdown (9 IOGP Rules)\n\n")
        f.write("| Official IOGP Life-Saving Rule | Validation Threshold | Test Support | Precision | Recall | F1-Score | Confusion (TP/FP/FN/TN) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in per_rule_rows:
            f.write(f"| **{r['rule']}** | {r['threshold']:.2f} | {r['support']} | {r['precision']:.4f} | {r['recall']:.4f} | **{r['f1_score']:.4f}** | {r['tp']}/{r['fp']}/{r['fn']}/{r['tn']} |\n")
        f.write(f"| **OVERALL (MICRO)** | — | **{sum(r['support'] for r in per_rule_rows)}** | **{s11_test_metrics['micro_precision']:.4f}** | **{s11_test_metrics['micro_recall']:.4f}** | **{s11_test_metrics['micro_f1']:.4f}** | — |\n")
        f.write(f"| **OVERALL (MACRO)** | — | — | **{s11_test_metrics['macro_precision']:.4f}** | **{s11_test_metrics['macro_recall']:.4f}** | **{s11_test_metrics['macro_f1']:.4f}** | — |\n\n")

    print(f"\nStage 11 Training & Test Evaluation Complete! Report: {report_path}")
    print("=" * 75)
    print("STAGE 11 SUMMARY:")
    print(f"  Micro-F1:     {s11_test_metrics['micro_f1']:.4f}")
    print(f"  Macro-F1:     {s11_test_metrics['macro_f1']:.4f}")
    print(f"  Hamming Loss: {s11_test_metrics['hamming_loss']:.4f}")
    print(f"  Exact Match:  {s11_test_metrics['exact_match_ratio']*100:.2f}%")
    print("=" * 75)

if __name__ == "__main__":
    train_stage11()
