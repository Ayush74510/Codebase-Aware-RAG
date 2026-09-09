# RRF = Reciprocal Rank Fusion

# Instead of asking:
#   "What was the score?"
# RRF asks:
#   "Where did this document rank?"

# Its purpose is to control how aggressively rank position affects the score.
#   Think of k as a rank smoothing parameter.

# Dense
# └── cosine distance

# BM25
# └── lexical relevance score





from __future__ import annotations
from dataclasses import replace
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.retriever import RetrievedChunk, Retriever


class HybridRetriever:
    """Combine dense and BM25 retrieval using Reciprocal Rank Fusion."""

    def __init__(
        self,
        dense_retriever: Retriever,
        bm25_retriever: BM25Retriever,
        rrf_k: int = 60,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError("rrf_k must be greater than 0.")

        self._dense_retriever = dense_retriever
        self._bm25_retriever = bm25_retriever
        self._rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the top-k chunks using hybrid retrieval."""

        if not query.strip():
            raise ValueError("Query must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        dense_results = self._dense_retriever.search(
            query=query,
            top_k=top_k,
        )

        bm25_results = self._bm25_retriever.search(
            query=query,
            top_k=top_k,
        )

        fused_scores: dict[int, float] = {}
        chunks_by_id: dict[int, RetrievedChunk] = {}

        for rank, chunk in enumerate(dense_results, start=1):
            fused_scores[chunk.id] = fused_scores.get(chunk.id, 0.0)
            fused_scores[chunk.id] += 1 / (self._rrf_k + rank)
            chunks_by_id[chunk.id] = chunk

        for rank, chunk in enumerate(bm25_results, start=1):
            fused_scores[chunk.id] = fused_scores.get(chunk.id, 0.0)
            fused_scores[chunk.id] += 1 / (self._rrf_k + rank)
            chunks_by_id[chunk.id] = chunk

        ranked_ids = sorted(
            fused_scores,
            key=fused_scores.get,
            reverse=True,
        )

        return [
            replace(
                chunks_by_id[chunk_id],
                score=fused_scores[chunk_id],
            )
            for chunk_id in ranked_ids[:top_k]
        ]