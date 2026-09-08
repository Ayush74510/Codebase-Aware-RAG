from src.embedding.embedder import CodeEmbedder

def test_embed_documents():
    embedder = CodeEmbedder()

    texts = [
        "def add(a, b): return a + b",
        "def subtract(a, b): return a - b",
    ]

    embeddings = embedder.embed_documents(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 1024
    assert len(embeddings[1]) == 1024