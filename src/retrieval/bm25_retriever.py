from __future__ import annotations
import re
from rank_bm25 import BM25Okapi # type: ignore

from src.database.connection import get_connection
from src.retrieval.retriever import RetrievedChunk


class BM25Retriever:
    """Retrieve code chunks using BM25 lexical search."""

    def __init__(self) -> None:
        self._chunks: list[RetrievedChunk] = []
        self._bm25: BM25Okapi | None = None

        self._build_index()

    def _build_index(self) -> None:
        """Load chunks from PostgreSQL and build the BM25 index."""

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        file_path,
                        chunk_type,
                        name,
                        content,
                        start_line,
                        end_line,
                        language,
                        metadata
                    FROM code_chunks
                    ORDER BY id
                    """
                )

                rows = cursor.fetchall()

        self._chunks = [
            RetrievedChunk(
                id=row[0],
                file_path=row[1],
                chunk_type=row[2],
                name=row[3],
                content=row[4],
                start_line=row[5],
                end_line=row[6],
                language=row[7],
                metadata=row[8],
                score=0.0,
            )
            for row in rows
        ]

        tokenized_documents = [
            self._tokenize(
                " ".join(
                    [
                        chunk.file_path,
                        chunk.chunk_type,
                        chunk.name,
                        chunk.metadata.get("parent_class") or "",
                        chunk.metadata.get("parent_function") or "",
                        chunk.content,
                    ]
                )
            )
            for chunk in self._chunks
        ]

        self._bm25 = BM25Okapi(tokenized_documents)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenize source code for lexical matching."""

        return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text.lower())

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the top-k chunks matching the query lexically."""

        if not query.strip():
            raise ValueError("Query must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if self._bm25 is None:
            return []

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        scores = self._bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results: list[RetrievedChunk] = []

        for index in ranked_indices[:top_k]:
            chunk = self._chunks[index]

            results.append(
                RetrievedChunk(
                    id=chunk.id,
                    file_path=chunk.file_path,
                    chunk_type=chunk.chunk_type,
                    name=chunk.name,
                    content=chunk.content,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    language=chunk.language,
                    metadata=chunk.metadata,
                    score=float(scores[index]),
                )
            )

        return results