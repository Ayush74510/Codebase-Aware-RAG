from src.embedding.embedder import CodeEmbedder
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.retriever import Retriever


embedder = CodeEmbedder()

dense_retriever = Retriever(embedder)
bm25_retriever = BM25Retriever()

query = "get_connection"

dense_results = dense_retriever.search(
    query,
    top_k=5,
)

bm25_results = bm25_retriever.search(
    query,
    top_k=5,
)

print("\n=== DENSE RESULTS ===")

for result in dense_results:
    print(
        f"{result.file_path} | "
        f"{result.name} | "
        f"distance={result.score:.4f}"
    )

print("\n=== BM25 RESULTS ===")

for result in bm25_results:
    print(
        f"{result.file_path} | "
        f"{result.name} | "
        f"score={result.score:.4f}"
    )