from app.embeddings.chunker import chunk_file, MAX_LINES_PER_CHUNK
from app.embeddings.service import embed_texts, embed_query, EMBEDDING_DIM


# --- Chunker tests ---

def test_chunk_empty_file():
    assert chunk_file("") == []


def test_chunk_small_file_single_chunk():
    content = "def foo():\n    return 1\n"
    chunks = chunk_file(content)
    assert len(chunks) == 1
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 2


def test_chunk_large_file_multiple_chunks():
    # 200 lines should produce multiple chunks
    lines = [f"line_{i} = {i}" for i in range(200)]
    content = "\n".join(lines)
    chunks = chunk_file(content)
    assert len(chunks) > 1
    # Each chunk must be within bounds (start < end, both >= 1)
    for chunk in chunks:
        assert chunk.start_line >= 1
        assert chunk.end_line >= chunk.start_line


def test_chunk_preserves_content():
    content = "a = 1\nb = 2\nc = 3\n"
    chunks = chunk_file(content)
    assert any("a = 1" in c.content for c in chunks)


def test_chunk_line_numbers_are_sequential():
    lines = [f"x = {i}" for i in range(150)]
    content = "\n".join(lines)
    chunks = chunk_file(content)
    # First chunk always starts at line 1
    assert chunks[0].start_line == 1
    # Last chunk always ends at or before total line count
    total = len(lines)
    assert chunks[-1].end_line <= total


# --- Embedding tests ---

def test_embed_texts_returns_correct_dimension():
    vectors = embed_texts(["def main(): pass"])
    assert len(vectors) == 1
    assert len(vectors[0]) == EMBEDDING_DIM


def test_embed_texts_empty_input():
    assert embed_texts([]) == []


def test_embed_query_returns_correct_dimension():
    vector = embed_query("How is authentication implemented?")
    assert len(vector) == EMBEDDING_DIM


def test_embed_texts_batch():
    texts = ["hello world", "def foo(): pass", "import os"]
    vectors = embed_texts(texts)
    assert len(vectors) == 3
    assert all(len(v) == EMBEDDING_DIM for v in vectors)
