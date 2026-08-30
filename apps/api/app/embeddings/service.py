from typing import List
import numpy as np

# Lazy import to avoid loading the model until first use (keeps startup fast)
_model = None
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # Dimension produced by all-MiniLM-L6-v2


def _get_model():
    """
    Lazily loads the sentence-transformers model on first call.
    This avoids a ~400ms startup penalty for endpoints that don't need embeddings.
    """
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generates 384-dimensional dense vector embeddings for a list of text strings.

    Uses the all-MiniLM-L6-v2 model which is:
    - Small (~80MB)
    - Fast on CPU
    - Good general-purpose semantic similarity for code and prose
    - 384-dimensional output compatible with our pgvector column

    Args:
        texts: A list of text strings to embed.

    Returns:
        A list of float vectors, one per input text.
    """
    if not texts:
        return []

    model = _get_model()
    embeddings: np.ndarray = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # Normalize so cosine similarity = dot product
    )
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Embeds a single query string for retrieval comparison.

    Args:
        query: The natural-language question to embed.

    Returns:
        A 384-dimensional float vector.
    """
    results = embed_texts([query])
    return results[0] if results else []
