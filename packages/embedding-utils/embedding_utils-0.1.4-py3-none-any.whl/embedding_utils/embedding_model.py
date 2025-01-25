import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from device_selector import check_or_select_device

from .embedding_cache import EmbeddingCache


class EmbeddingModel:
    def __init__(
        self,
        model_name: str = None,
        device: Optional[str] = None,
        cache_path: str = None
    ):
        """
        A simple wrapper around SentenceTransformer + caching.
        :param model_name: The sentence-transformers model name or path.
        :param device: 'cpu', 'cuda', or 'mps' etc.
        :param cache_path: If given, load/save embeddings here to avoid re-computation.
        """
        self.model_name = model_name
        self.device = check_or_select_device(device)
        self.cache = EmbeddingCache(cache_path)
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode_texts(self, texts: List[str], show_progress_bar: bool = True) -> List[np.ndarray]:
        """
        Retrieves or computes embeddings for a batch of texts, leveraging caching.
        """
        embeddings = []
        to_encode = []
        to_encode_idxs = []

        # 1) Check cache
        for idx, txt in enumerate(texts):
            cached = self.cache.get_embedding(txt)
            if cached is not None:
                embeddings.append(cached)
            else:
                embeddings.append(None)
                to_encode.append(txt)
                to_encode_idxs.append(idx)

        # 2) Encode if needed
        if to_encode:
            new_embs = self.model.encode(to_encode, device=self.device, show_progress_bar=show_progress_bar)
            # 3) Store them in cache
            for i, emb in enumerate(new_embs):
                actual_idx = to_encode_idxs[i]
                txt = to_encode[i]
                self.cache.set_embedding(txt, emb)
                embeddings[actual_idx] = emb

        return embeddings

    @staticmethod
    def compute_cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity in [0..1].
        """
        return float(
            np.dot(emb1, emb2)
            / ((np.linalg.norm(emb1) * np.linalg.norm(emb2)) + 1e-9)
        )

    def save_cache(self):
        """If you want to save the cache explicitly."""
        self.cache.save_cache()
