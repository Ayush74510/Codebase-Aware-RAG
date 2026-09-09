from __future__ import annotations
from dataclasses import dataclass
from src.database.connection import get_connection
from src.embedding.embedder import CodeEmbedder
from pgvector import Vector # type: ignore


@dataclass
class RetrievedChunk:
    """A code chunk returned by semantic search."""

    id: int
    file_path: str
    chunk_type: str
    name: str
    content: str
    start_line: int
    end_line: int
    language: str | None
    metadata: dict
    score: float


class Retriever:
    """Retrieve the most semantically relevant code chunks."""

    def __init__(self, embedder: CodeEmbedder) -> None:
        self._embedder = embedder

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the top-k code chunks relevant to a query."""

        if not query.strip():
            raise ValueError("Query must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        query_embedding = Vector(self._embedder.embed_query(query))    

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
                        metadata,
                        embedding <=> %s AS score
                    FROM code_chunks
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (
                        query_embedding,
                        query_embedding,
                        top_k,
                    ),
                )

                rows = cursor.fetchall()

        return [
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
                score=float(row[9]),
            )
            for row in rows
        ]