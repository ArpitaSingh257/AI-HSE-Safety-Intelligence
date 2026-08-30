"""
sif_predictor.py - Standalone SIF Binary Classification Predictor.
Robustly supports both Stage 6 Champion and Stage 4 baseline checkpoints with auto-inferred dimensions and layer key adaptation.
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

class SIFDynamicAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        # Define both naming conventions for seamless state_dict loading
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        self.attention = self.attn
        
    def forward(self, gru_outputs, mask=None):
        weights = self.attn(gru_outputs)
        if mask is not None:
            weights = weights.masked_fill(mask.unsqueeze(-1) == 0, -1e9)
        attn_weights = F.softmax(weights, dim=1)
        context = torch.sum(attn_weights * gru_outputs, dim=1)
        return context, attn_weights.squeeze(-1)

class SIFAdaptiveModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=200, hidden_dim=128, dropout=0.2, pad_idx=0):
        super().__init__()
        self.pad_idx = pad_idx
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.dropout = nn.Dropout(dropout)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attention = SIFDynamicAttention(hidden_dim * 2)
        self.fc = nn.Linear(hidden_dim * 2, 1)
        
    def forward(self, x):
        mask = (x != self.pad_idx)
        embeds = self.dropout(self.embedding(x))
        gru_out, _ = self.gru(embeds)
        context, attn_weights = self.attention(gru_out, mask=mask)
        logits = self.fc(self.dropout(context))
        return logits, attn_weights

class SIFPredictor:
    """Production Predictor for SIF (Serious Injury & Fatality) Precursor Detection."""
    def __init__(self, model_dir: str = None, device: str = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
            
        base_dir = Path(__file__).resolve().parent.parent
        
        possible_ckpts = [
            base_dir / "models" / "sif" / "sif_model.pt",
            base_dir / "results" / "gru_optimization" / "best_sif_model" / "sif_optimized_gru_attention.pt",
            base_dir / "results" / "gru" / "sif" / "gru_attention" / "best_sif_gru_attention.pt"
        ]
        
        possible_cfgs = [
            base_dir / "models" / "sif" / "sif_config.json",
            base_dir / "results" / "gru_optimization" / "best_sif_config.json"
        ]
        
        possible_vocabs = [
            base_dir / "models" / "sif" / "sif_vocab.json",
            base_dir / "results" / "gru" / "sif" / "sif_vocab.json"
        ]
        
        if model_dir is not None:
            custom_dir = Path(model_dir)
            possible_ckpts.insert(0, custom_dir / "sif_model.pt")
            possible_cfgs.insert(0, custom_dir / "sif_config.json")
            possible_vocabs.insert(0, custom_dir / "sif_vocab.json")
            
        # Locate Checkpoint
        ckpt_path = None
        for p in possible_ckpts:
            if p.exists():
                ckpt_path = p
                break
                
        # Locate Config
        cfg_path = None
        for p in possible_cfgs:
            if p.exists():
                cfg_path = p
                break
                
        # Locate Vocab
        vocab_path = None
        for p in possible_vocabs:
            if p.exists():
                vocab_path = p
                break
                
        self.threshold = 0.30
        self.max_len = 120
        self.dropout = 0.2
        
        if cfg_path is not None and cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                self.threshold = float(cfg.get("tuned_validation_threshold", 0.30))
                self.dropout = float(cfg.get("dropout", 0.2))
                
        # Load Vocab
        if vocab_path is not None and vocab_path.exists():
            self.vocab = InferenceVocabulary(vocab_path)
        else:
            train_csv = base_dir / "datasets" / "model_ready" / "splits" / "sif_train.csv"
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
                
        # Adaptively inspect Checkpoint State Dict
        self.has_trained_weights = False
        self.checkpoint_loaded_from = "NOT_LOADED"
        
        if ckpt_path is not None and ckpt_path.exists():
            state_dict = torch.load(ckpt_path, map_location="cpu")
            
            # Infer exact dimensions from state_dict
            embed_weight = state_dict.get("embedding.weight", None)
            gru_hh_weight = state_dict.get("gru.weight_hh_l0", None)
            
            vocab_size = embed_weight.shape[0] if embed_weight is not None else self.vocab.vocab_size
            embed_dim = embed_weight.shape[1] if embed_weight is not None else 200
            hidden_dim = gru_hh_weight.shape[1] if gru_hh_weight is not None else 128
            
            # Remap attention layer keys if necessary
            adapted_state = {}
            for k, v in state_dict.items():
                if k.startswith("attention.attention."):
                    adapted_state[k.replace("attention.attention.", "attention.attn.")] = v
                elif k.startswith("attention.attn."):
                    adapted_state[k] = v
                else:
                    adapted_state[k] = v
                    
            self.model = SIFAdaptiveModel(
                vocab_size=vocab_size,
                embed_dim=embed_dim,
                hidden_dim=hidden_dim,
                dropout=self.dropout
            ).to(self.device)
            
            self.model.load_state_dict(adapted_state, strict=False)
            self.has_trained_weights = True
            self.checkpoint_loaded_from = str(ckpt_path)
            self.embed_dim = embed_dim
            self.hidden_dim = hidden_dim
        else:
            self.model = SIFAdaptiveModel(
                vocab_size=self.vocab.vocab_size,
                embed_dim=200,
                hidden_dim=128,
                dropout=self.dropout
            ).to(self.device)
            
        self.model.eval()
        
    def predict(self, narrative: str) -> dict:
        """Predict SIF probability and label for an incident narrative."""
        if not isinstance(narrative, str) or not narrative.strip():
            return {
                "sif_probability": 0.0,
                "sif_label": 0,
                "threshold": self.threshold,
                "model": "optimized_bigru_attention",
                "checkpoint_loaded": self.has_trained_weights,
                "top_attended_tokens": []
            }
            
        tensor_in, tokens = self.vocab.text_to_tensor(narrative, max_len=self.max_len, device=self.device)
        
        with torch.no_grad():
            logits, attn_weights = self.model(tensor_in)
            prob = float(torch.sigmoid(logits.squeeze(-1)).item())
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
            
        sif_label = 1 if prob >= self.threshold else 0
        
        return {
            "sif_probability": float(np.round(prob, 4)),
            "sif_label": int(sif_label),
            "threshold": float(self.threshold),
            "model": "optimized_bigru_attention",
            "checkpoint_loaded": self.has_trained_weights,
            "top_attended_tokens": top_attns
        }
