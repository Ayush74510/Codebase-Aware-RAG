from src.embedding.embedder import CodeEmbedder
from src.retrieval.retriever import Retriever


embedder = CodeEmbedder()
retriever = Retriever(embedder)

results = retriever.search(
    "Where is the PostgreSQL database connection created?",
    top_k=5,
)

print(f"Found {len(results)} results\n")

for result in results:
    print(
        f"[{result.distance:.4f}] "
        f"{result.file_path}:{result.start_line}-{result.end_line}"
    )
    print(f"  {result.chunk_type}: {result.name}")
    print()