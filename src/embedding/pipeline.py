# CodeEmbedder
#     → embedding

# ChunkStore
#     → database

# EmbeddingPipeline
#     → orchestration


from __future__ import annotations
from src.database.chunk_store import ChunkStore
from src.embedding.embedder import CodeEmbedder
from src.ingestion.ast_chunker import CodeChunk


class EmbeddingPipeline:
    """Embed code chunks and store them in PostgreSQL."""

    def __init__(
        self,
        embedder: CodeEmbedder,
        store: ChunkStore,
        batch_size: int = 32,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0.")

        self._embedder = embedder
        self._store = store
        self._batch_size = batch_size

    def process(self, chunks: list[CodeChunk], repository_id:str) -> int:
        """Embed and store all code chunks.

        Returns:
            Number of chunks successfully stored.
        """

        stored_count = 0

        for start in range(0, len(chunks), self._batch_size):
            batch = chunks[start:start + self._batch_size]

            texts = [chunk.content for chunk in batch]

            embeddings = self._embedder.embed_documents(texts)

            if len(embeddings) != len(batch):
                raise RuntimeError(
                    "Number of embeddings does not match number of chunks."
                )

            for chunk, embedding in zip(batch, embeddings):
                self._store.insert_chunk(chunk, embedding, repository_id)
                stored_count += 1

        return stored_count