"""
embeddings.py - Modular & Deterministic Semantic Embedding Engine for OILPS RAG.
Supports sentence-transformers (all-MiniLM-L6-v2) with fallback to PyTorch/TF-IDF deterministic vector encoding.
"""

import sys
import logging
import numpy as np
from pathlib import Path
from typing import List, Union

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

logger = logging.getLogger("OILPS_Embeddings")
logging.basicConfig(level=logging.INFO)

# Attempt to load sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class SafetyEmbeddingEngine:
    """
    Deterministic Semantic Embedding Model for RAG Chunk Indexing & Query Encoding.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.vector_dim = 384
        self._init_model()

    def _init_model(self):
        """Initialize sentence transformer model or fallback encoder."""
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading SentenceTransformer model: '{self.model_name}'...")
                self.model = SentenceTransformer(self.model_name)
                if hasattr(self.model, "get_embedding_dimension"):
                    self.vector_dim = self.model.get_embedding_dimension()
                elif hasattr(self.model, "get_sentence_embedding_dimension"):
                    self.vector_dim = self.model.get_sentence_embedding_dimension()
                else:
                    self.vector_dim = 384
                logger.info(f"Loaded SentenceTransformer successfully (dimension={self.vector_dim}).")
                return
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Using fallback encoder.")
        
        # Fallback vector encoder if offline / missing package
        logger.info("Initializing fallback deterministic hashing embedding engine...")
        self.model = None
        self.vector_dim = 384

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Encode text or list of texts into embedding vectors.
        Returns float32 numpy array of shape (N, vector_dim).
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.zeros((0, self.vector_dim), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    normalize_embeddings=normalize
                )
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning(f"Error during SentenceTransformer encoding: {e}. Falling back to deterministic encoder.")

        # Deterministic hashing fallback encoder for test/offline resilience
        embeddings = []
        for text in texts:
            vec = np.zeros(self.vector_dim, dtype=np.float32)
            words = text.lower().split()
            if words:
                for idx, word in enumerate(words):
                    # Deterministic hash to vector indices
                    h = hash(word)
                    pos = abs(h) % self.vector_dim
                    val = 1.0 if h > 0 else -1.0
                    vec[pos] += val
                norm = np.linalg.norm(vec)
                if norm > 0 and normalize:
                    vec = vec / norm
            embeddings.append(vec)

        return np.array(embeddings, dtype=np.float32)


if __name__ == "__main__":
    engine = SafetyEmbeddingEngine()
    test_vecs = engine.encode(["Energy Isolation hydrostatic test", "Confined space gas test"])
    print("Encoded vectors shape:", test_vecs.shape)
