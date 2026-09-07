from src.database.chunk_store import ChunkStore
from src.embedding.embedder import CodeEmbedder
from src.ingestion.ast_chunker import CodeChunk
from src.ingestion.metadata import ChunkMetadata


chunk = CodeChunk(
    file_path="test/example.py",
    chunk_type="function",
    name="add",
    content="def add(a, b):\n    return a + b",
    start_line=1,
    end_line=2,
    language="python",
    metadata=ChunkMetadata(
        decorators=[],
        imports=[],
        calls=[],
    ),
)

embedder = CodeEmbedder()

embedding = embedder.embed_documents(
    [chunk.content]
)[0]

store = ChunkStore()

chunk_id = store.insert_chunk(
    chunk,
    embedding,
)

print("Inserted chunk ID:", chunk_id)