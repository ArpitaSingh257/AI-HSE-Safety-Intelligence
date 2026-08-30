"""
preprocessing.py - Text preprocessing & vocabulary indexing utilities for production inference.
"""

import re
import json
import torch
from pathlib import Path
from collections import Counter

def clean_and_tokenize(text: str) -> list[str]:
    """Clean and lower-case narrative text, stripping punctuation."""
    if not isinstance(text, str) or not text.strip():
        return []
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()

class InferenceVocabulary:
    """Production vocabulary loader for inference mapping."""
    def __init__(self, vocab_dict_or_path, pad_idx=0, unk_idx=1):
        self.pad_idx = pad_idx
        self.unk_idx = unk_idx
        self.pad_token = "<PAD>"
        self.unk_token = "<UNK>"
        
        if isinstance(vocab_dict_or_path, (str, Path)):
            with open(vocab_dict_or_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.word2idx = data.get("word2idx", data)
        else:
            self.word2idx = vocab_dict_or_path
            
        self.idx2word = {v: k for k, v in self.word2idx.items()}
        self.vocab_size = len(self.word2idx)
        
    def text_to_tensor(self, text: str, max_len: int = 120, device: torch.device = None) -> tuple[torch.Tensor, list[str]]:
        tokens = clean_and_tokenize(text)
        truncated_tokens = tokens[:max_len]
        indices = [self.word2idx.get(w, self.unk_idx) for w in truncated_tokens]
        if len(indices) < max_len:
            indices += [self.pad_idx] * (max_len - len(indices))
        tensor = torch.tensor([indices], dtype=torch.long)
        if device is not None:
            tensor = tensor.to(device)
        return tensor, truncated_tokens
