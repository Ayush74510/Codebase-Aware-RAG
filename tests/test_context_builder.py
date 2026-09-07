from src.embedding.embedder import CodeEmbedder
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.retriever import Retriever


embedder = CodeEmbedder()
retriever = Retriever(embedder)

results = retriever.search(
    "Where is the PostgreSQL database connection created?",
    top_k=3,
)

context = ContextBuilder.build(results)

print(context)