from __future__ import annotations
from src.embedding.embedder import CodeEmbedder
from src.embedding.pipeline import EmbeddingPipeline
from src.database.chunk_store import ChunkStore
from src.ingestion.ast_chunker import ASTChunker
from src.ingestion.repo_loader import RepositoryLoader


def index_repository(source: str) -> int:
    """Load, chunk, embed, and store a repository."""

    loader = RepositoryLoader()
    repository_files = loader.load(source)

    chunker = ASTChunker()
    
    chunks = []
    for repository_file in repository_files:
        chunks.extend(chunker.chunk(repository_file))

    embedder = CodeEmbedder()
    store = ChunkStore()

    pipeline = EmbeddingPipeline(
        embedder=embedder,
        store=store,
    )

    return pipeline.process(chunks)
