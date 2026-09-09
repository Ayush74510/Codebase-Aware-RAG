# This tests -> bge-m3
#                 ↓
#                 PostgreSQL / pgvector ──┐
#                                         ├── RRF
#                 PostgreSQL → BM25 ──────┘
#                                         ↓
#                                     hybrid results






from src.embedding.embedder import CodeEmbedder
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.retriever import Retriever


def test_hybrid_retriever_finds_database_connection():
    embedder = CodeEmbedder()

    dense_retriever = Retriever(embedder)
    bm25_retriever = BM25Retriever()

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        bm25_retriever=bm25_retriever,
    )

    results = hybrid_retriever.search(
        "Where is the PostgreSQL database connection created?",
        top_k=5,
    )

    assert results

    assert any(
        result.file_path == "src/database/connection.py"
        and result.name == "get_connection"
        for result in results
    )
    
    
    
    