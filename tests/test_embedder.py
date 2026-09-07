from src.embedding.embedder import CodeEmbedder


embedder = CodeEmbedder()

embeddings = embedder.embed_documents(
    [
        "def add(a, b): return a + b",
        "def multiply(a, b): return a * b",
    ]
)

print("Number of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))