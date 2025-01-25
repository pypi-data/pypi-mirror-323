import pytest
import tempfile
import os

from embedding_utils import EmbeddingModel


def test_cache_round_trip():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = os.path.join(tmpdir, "emb_cache.pkl")

        model1 = EmbeddingModel(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
            cache_path=cache_path
        )
        texts = ["Hello world", "Another phrase"]
        # First encode
        embs1 = model1.encode_texts(texts)
        model1.save_cache()

        # Re-instantiate new model with the same cache
        model2 = EmbeddingModel(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
            cache_path=cache_path
        )
        # Should load from cache
        embs2 = model2.encode_texts(texts)

        for e1, e2 in zip(embs1, embs2):
            # They should be identical arrays
            assert (e1 == e2).all()

def test_cosine_similarity():
    model = EmbeddingModel(model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    emb1 = [1.0, 0.0, 0.0]
    emb2 = [1.0, 0.0, 0.0]
    sim = model.compute_cosine_similarity(emb1, emb2)
    assert sim == pytest.approx(1.0, 1e-6)

    emb3 = [0.0, 1.0, 0.0]
    sim_diff = model.compute_cosine_similarity(emb1, emb3)
    assert sim_diff < 0.1  # or whatever threshold
