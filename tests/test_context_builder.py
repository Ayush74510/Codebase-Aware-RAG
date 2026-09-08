from src.retrieval.context_builder import ContextBuilder
from src.retrieval.retriever import RetrievedChunk


def test_context_builder_formats_chunks():
    chunk = RetrievedChunk(
        id=1,
        file_path="src/database/connection.py",
        chunk_type="function",
        name="get_connection",
        content="connection = psycopg.connect(DATABASE_URL)",
        start_line=20,
        end_line=21,
        language="python",
        metadata={},
        distance=0.1,
    )

    context = ContextBuilder.build([chunk])

    assert "src/database/connection.py" in context
    assert "get_connection" in context
    assert "20-21" in context
    assert "connection = psycopg.connect(DATABASE_URL)" in context
    assert "```python" in context