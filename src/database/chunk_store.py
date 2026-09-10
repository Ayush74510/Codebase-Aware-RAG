#  → responsible ONLY for PostgreSQL

# CodeChunk + embedding
#         ↓
# PostgreSQL code_chunks

from __future__ import annotations
import json
from src.database.connection import get_connection
from src.ingestion.ast_chunker import CodeChunk


class ChunkStore:
    """Store code chunks and their embeddings in PostgreSQL."""

    def insert_chunk(
        self,
        chunk: CodeChunk,
        embedding: list[float],
        repository_id: str,
    ) -> int:
        """Insert one code chunk and its embedding.

        Returns:
            The database ID assigned to the inserted chunk.
        """

        metadata = json.dumps(
            {
                "parent_class": chunk.metadata.parent_class,
                "parent_function": chunk.metadata.parent_function,
                "decorators": chunk.metadata.decorators,
                "imports": chunk.metadata.imports,
                "calls": chunk.metadata.calls,
            }
        )

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO code_chunks (
                        file_path,
                        chunk_type,
                        name,
                        content,
                        start_line,
                        end_line,
                        language,
                        metadata,
                        embedding,
                        repository_id
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::jsonb,
                        %s,
                        %s
                    )
                    ON CONFLICT (
                        repository_id,
                        file_path,
                        chunk_type,
                        name,
                        start_line,
                        end_line
                    )
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        language = EXCLUDED.language,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding
                    RETURNING id    
                    """,
                    (
                        chunk.file_path,
                        chunk.chunk_type,
                        chunk.name,
                        chunk.content,
                        chunk.start_line,
                        chunk.end_line,
                        chunk.language,
                        metadata,
                        embedding,
                        repository_id,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Failed to retrieve inserted chunk ID."
                    )

                return row[0]
            
    def delete_repository(self, repository_id: str) -> int:
        """Delete all chunks belonging to a repository."""
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM code_chunks
                    WHERE repository_id = %s
                    """,
                    (repository_id,),
                )
                return cursor.rowcount