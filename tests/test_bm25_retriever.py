from src.retrieval.bm25_retriever import BM25Retriever


def test_bm25_finds_exact_identifier():
    retriever = BM25Retriever()

    results = retriever.search(
        "get_connection",
        top_k=5,
    )

    assert results

    assert any(
        result.file_path == "src/database/connection.py"
        and result.name == "get_connection"
        for result in results
    )