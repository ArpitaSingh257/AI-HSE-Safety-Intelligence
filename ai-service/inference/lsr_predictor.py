"""
lsr_predictor.py - Standalone Multi-Label Life-Saving Rules Predictor.
Robustly supports Stage 7 Champion, Stage 6, and Stage 4 checkpoints with auto-inferred dimensions and layer adaptations.
"""

import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from .preprocessing import InferenceVocabulary, clean_and_tokenize

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

class LSRDynamicAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.proj = nn.Linear(hidden_dim, 128)
        self.score = nn.Linear(128, 1, bias=False)
        self.scale = np.sqrt(128)
        # Alternate 2-layer MLP naming
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        
    def forward(self, gru_outputs, mask=None):
        energy = torch.tanh(self.proj(gru_outputs))
        weights = self.score(energy) / self.scale
        if mask is not None:
            weights = weights.masked_fill(mask.unsqueeze(-1) == 0, -1e9)
        attn_weights = F.softmax(weights, dim=1)
        context = torch.sum(attn_weights * gru_outputs, dim=1)
        return context, attn_weights.squeeze(-1)

class LSRAdaptiveModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=200, hidden_dim=128, num_classes=9, dropout=0.25, pad_idx=0):
        super().__init__()
        self.pad_idx = pad_idx
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.embed_dropout = nn.Dropout(dropout)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        eff_hidden = hidden_dim * 2
        self.layer_norm = nn.LayerNorm(eff_hidden)
        self.attention = LSRDynamicAttention(eff_hidden)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(eff_hidden, 128),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, num_classes)
        )
        self.fc = nn.Linear(eff_hidden, num_classes)
        
    def forward(self, x):
        mask = (x != self.pad_idx)
        embeds = self.embed_dropout(self.embedding(x))
        gru_out, _ = self.gru(embeds)
        norm_gru_out = self.layer_norm(gru_out)
        context, attn_weights = self.attention(norm_gru_out, mask=mask)
        logits = self.classifier(context)
        return logits, attn_weights

class LSRPredictor:
    """Production Multi-Label Predictor for 9 IOGP Life-Saving Rules."""
    def __init__(self, model_dir: str = None, device: str = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        base_dir = Path(__file__).resolve().parent.parent
        self.rule_names = OFFICIAL_9_LSR
        
        self.rule_thresholds = {
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
        
        possible_ckpts = [
            base_dir / "models" / "lsr" / "lsr_model.pt",
            base_dir / "results" / "lsr_stage7" / "checkpoints" / "best_lsr_stage7_model.pt",
            base_dir / "results" / "gru_optimization" / "best_lsr_model" / "lsr_optimized_gru_attention.pt",
            base_dir / "results" / "gru" / "lsr" / "gru_attention" / "best_lsr_gru_attention.pt"
        ]
        
        possible_cfgs = [
            base_dir / "models" / "lsr" / "lsr_config.json",
            base_dir / "results" / "lsr_stage7" / "stage7_lsr_config.json",
            base_dir / "results" / "gru_optimization" / "best_lsr_config.json"
        ]
        
        possible_vocabs = [
            base_dir / "models" / "lsr" / "lsr_vocab.json",
            base_dir / "results" / "gru" / "lsr" / "lsr_vocab.json"
        ]
        
        if model_dir is not None:
            custom_dir = Path(model_dir)
            possible_ckpts.insert(0, custom_dir / "lsr_model.pt")
            possible_cfgs.insert(0, custom_dir / "lsr_config.json")
            possible_vocabs.insert(0, custom_dir / "lsr_vocab.json")
            
        ckpt_path = None
        for p in possible_ckpts:
            if p.exists():
                ckpt_path = p
                break
                
        cfg_path = None
        for p in possible_cfgs:
            if p.exists():
                cfg_path = p
                break
                
        vocab_path = None
        for p in possible_vocabs:
            if p.exists():
                vocab_path = p
                break
                
        self.dropout = 0.25
        self.max_len = 120
        
        if cfg_path is not None and cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                loaded_thresh = cfg.get("per_rule_thresholds", None)
                if loaded_thresh:
                    self.rule_thresholds.update({k: float(v) for k, v in loaded_thresh.items() if k in self.rule_names})
                self.dropout = float(cfg.get("dropout", 0.25))
                
        if vocab_path is not None and vocab_path.exists():
            self.vocab = InferenceVocabulary(vocab_path)
        else:
            train_csv = base_dir / "datasets" / "model_ready" / "splits" / "lsr_train.csv"
            if train_csv.exists():
                df = pd.read_csv(train_csv)
                texts = df["narrative"].fillna("").astype(str).tolist()
                counts = Counter()
                for t in texts:
                    counts.update(clean_and_tokenize(t))
                w2i = {"<PAD>": 0, "<UNK>": 1}
                for w, c in counts.items():
                    if c >= 2 and w not in w2i:
                        w2i[w] = len(w2i)
                self.vocab = InferenceVocabulary(w2i)
            else:
                self.vocab = InferenceVocabulary({"<PAD>": 0, "<UNK>": 1})
                
        self.has_trained_weights = False
        self.checkpoint_loaded_from = "NOT_LOADED"
        
        if ckpt_path is not None and ckpt_path.exists():
            state_dict = torch.load(ckpt_path, map_location="cpu")
            embed_weight = state_dict.get("embedding.weight", None)
            gru_hh_weight = state_dict.get("gru.weight_hh_l0", None)
            
            vocab_size = embed_weight.shape[0] if embed_weight is not None else self.vocab.vocab_size
            embed_dim = embed_weight.shape[1] if embed_weight is not None else 200
            hidden_dim = gru_hh_weight.shape[1] if gru_hh_weight is not None else 128
            
            self.model = LSRAdaptiveModel(
                vocab_size=vocab_size,
                embed_dim=embed_dim,
                hidden_dim=hidden_dim,
                dropout=self.dropout
            ).to(self.device)
            
            self.model.load_state_dict(state_dict, strict=False)
            self.has_trained_weights = True
            self.checkpoint_loaded_from = str(ckpt_path)
        else:
            self.model = LSRAdaptiveModel(
                vocab_size=self.vocab.vocab_size,
                embed_dim=200,
                hidden_dim=128,
                dropout=self.dropout
            ).to(self.device)
            
        self.model.eval()
        
    def predict(self, narrative: str) -> dict:
        """Predict multi-label Life-Saving Rules for an incident narrative."""
        if not isinstance(narrative, str) or not narrative.strip():
            return {
                "predicted_rules": [],
                "rule_probabilities": {r: 0.0 for r in self.rule_names},
                "rule_thresholds": {r: float(self.rule_thresholds.get(r, 0.50)) for r in self.rule_names},
                "checkpoint_loaded": self.has_trained_weights,
                "top_attended_tokens": []
            }
            
        tensor_in, tokens = self.vocab.text_to_tensor(narrative, max_len=self.max_len, device=self.device)
        
        with torch.no_grad():
            logits, attn_weights = self.model(tensor_in)
            probs = torch.sigmoid(logits[0]).cpu().numpy()
            raw_w = attn_weights[0].cpu().numpy()[:len(tokens)]
            if len(raw_w) > 0 and raw_w.sum() > 0:
                norm_w = raw_w / raw_w.sum()
            else:
                norm_w = raw_w
                
            top_attns = sorted(
                [{"token": str(t), "weight": float(np.round(w, 4))} for t, w in zip(tokens, norm_w)],
                key=lambda x: x["weight"],
                reverse=True
            )[:5]
            
        rule_probs = {}
        predicted_rules = []
        
        for idx, r_name in enumerate(self.rule_names):
            p = float(np.round(probs[idx], 4))
            rule_probs[r_name] = p
            thresh = float(self.rule_thresholds.get(r_name, 0.50))
            if p >= thresh:
                predicted_rules.append(r_name)
                
        return {
            "predicted_rules": predicted_rules,
            "rule_probabilities": rule_probs,
            "rule_thresholds": {k: float(v) for k, v in self.rule_thresholds.items()},
            "checkpoint_loaded": self.has_trained_weights,
            "top_attended_tokens": top_attns
        }
