from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.retriever import RetrievedChunk


def make_chunk(chunk_id: int, name: str) -> RetrievedChunk:
    return RetrievedChunk(
        id=chunk_id,
        file_path=f"file_{chunk_id}.py",
        chunk_type="function",
        name=name,
        content=f"def {name}(): pass",
        start_line=1,
        end_line=1,
        language="python",
        metadata={},
        score=0.0,
    )


class FakeRetriever:
    def __init__(self, results):
        self._results = results

    def search(self, query: str, top_k: int = 5):
        return self._results[:top_k]


def test_rrf_favors_documents_found_by_both_retrievers():
    shared_chunk = make_chunk(1, "shared")
    dense_only = make_chunk(2, "dense_only")
    bm25_only = make_chunk(3, "bm25_only")

    dense_retriever = FakeRetriever(
        [
            shared_chunk,
            dense_only,
        ]
    )

    bm25_retriever = FakeRetriever(
        [
            shared_chunk,
            bm25_only,
        ]
    )

    hybrid = HybridRetriever(
        dense_retriever=dense_retriever,
        bm25_retriever=bm25_retriever,
    )

    results = hybrid.search(
        query="test",
        top_k=3,
    )

    assert results
    assert results[0].id == 1
    assert results[0].name == "shared"