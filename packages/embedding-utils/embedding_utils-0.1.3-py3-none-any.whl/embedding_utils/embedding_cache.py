import pickle
import os
import numpy as np
from typing import Dict


class EmbeddingCache:
    """
    Manages a dictionary of text -> embedding vectors,
    providing load/save methods for serialization.
    """

    def __init__(self, cache_path: str = None):
        self.cache_path = cache_path
        self._cache: Dict[str, np.ndarray] = {}
        # If a cache file is provided, try to load it
        if cache_path and os.path.exists(cache_path):
            self.load_cache(cache_path)

    def get_embedding(self, text: str):
        """
        Return the embedding if it exists in the cache, otherwise None.
        """
        return self._cache.get(text)

    def set_embedding(self, text: str, embedding: np.ndarray):
        """
        Store an embedding in the in-memory cache.
        """
        self._cache[text] = embedding

    def save_cache(self, path: str = None):
        """
        Serialize the cache to disk with pickle.
        """
        if not path:
            path = self.cache_path
        if not path:
            return

        with open(path, "wb") as f:
            pickle.dump(self._cache, f)
        print(f"Embedding cache saved to {path}.")

    def load_cache(self, path: str = None):
        """
        Load the cache from disk using pickle.
        """
        if not path:
            path = self.cache_path
        if not path or not os.path.exists(path):
            return

        with open(path, "rb") as f:
            self._cache = pickle.load(f)
        print(f"Embedding cache loaded from {path}.")
