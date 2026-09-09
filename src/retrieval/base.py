from __future__ import annotations
from typing import Protocol
from src.retrieval.retriever import RetrievedChunk


class RetrieverProtocol(Protocol):
    """Interface required by the RAG pipeline for retrieval."""

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        ...