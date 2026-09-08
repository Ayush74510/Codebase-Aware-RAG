from src.embedding.embedder import CodeEmbedder
from src.retrieval.retriever import Retriever


def test_retriever_finds_database_connection():
    embedder = CodeEmbedder()
    retriever = Retriever(embedder)

    results = retriever.search(
        "Where is the PostgreSQL database connection created?",
        top_k=5,
    )

    assert results
    assert len(results) <= 5

    assert any(
        result.file_path == "src/database/connection.py"
        and result.name == "get_connection"
        for result in results
    )