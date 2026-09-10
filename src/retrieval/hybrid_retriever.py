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
import re
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
        dense_weight: float = 1.0,
        bm25_weight: float = 1.0,
    ) -> None:
        if rrf_k <= 0:
            raise ValueError("rrf_k must be greater than 0.")

        if dense_weight <= 0:
            raise ValueError("dense_weight must be greater than 0.")

        if bm25_weight <= 0:
            raise ValueError("bm25_weight must be greater than 0.")

        self._dense_retriever = dense_retriever
        self._bm25_retriever = bm25_retriever
        self._rrf_k = rrf_k
        self._dense_weight = dense_weight
        self._bm25_weight = bm25_weight

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
        
        if not self._is_identifier_query(query):
            return self._dense_retriever.search(
                query=query,
                top_k=top_k,
            )

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
            fused_scores[chunk.id] += (self._dense_weight / (self._rrf_k + rank))
            chunks_by_id[chunk.id] = chunk

        for rank, chunk in enumerate(bm25_results, start=1):
            fused_scores[chunk.id] = fused_scores.get(chunk.id, 0.0)
            fused_scores[chunk.id] += (self._bm25_weight / (self._rrf_k + rank))
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
        
    @staticmethod
    def _is_identifier_query(query: str) -> bool:
        """Return True when a query contains a code-style identifier."""
        return bool(
            re.search(
                r"\b[A-Za-z_][A-Za-z0-9]*_[A-Za-z0-9_]+\b",
                query,
            )
        )