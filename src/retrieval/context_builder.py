from __future__ import annotations
from src.retrieval.retriever import RetrievedChunk


class ContextBuilder:
    """Build an LLM-ready context from retrieved code chunks."""

    @staticmethod
    def build(chunks: list[RetrievedChunk]) -> str:
        """Format retrieved chunks into a context string."""

        if not chunks:
            return "No relevant code was found."

        sections: list[str] = []

        for chunk in chunks:
            sections.append(
                f"""File: {chunk.file_path}
Lines: {chunk.start_line}-{chunk.end_line}
Type: {chunk.chunk_type}
Name: {chunk.name}

```{chunk.language or ""}
{chunk.content}
```"""
            )

        return "\n\n---\n\n".join(sections)