from src.database.chunk_store import ChunkStore
from src.embedding.embedder import CodeEmbedder
from src.embedding.pipeline import EmbeddingPipeline
from src.ingestion.ast_chunker import CodeChunk
from src.ingestion.metadata import ChunkMetadata


chunks = [
    CodeChunk(
        file_path="test/math.py",
        chunk_type="function",
        name="add",
        content="def add(a, b):\n    return a + b",
        start_line=1,
        end_line=2,
        language="python",
        metadata=ChunkMetadata(),
    ),
    CodeChunk(
        file_path="test/math.py",
        chunk_type="function",
        name="multiply",
        content="def multiply(a, b):\n    return a * b",
        start_line=4,
        end_line=5,
        language="python",
        metadata=ChunkMetadata(),
    ),
]


embedder = CodeEmbedder()
store = ChunkStore()

pipeline = EmbeddingPipeline(
    embedder=embedder,
    store=store,
    batch_size=2,
)

stored_count = pipeline.process(chunks)

print("Stored chunks:", stored_count)