from __future__ import annotations
from src.generation.llm import CodeLLM
from src.retrieval.context_builder import ContextBuilder
from src.retrieval.base import RetrieverProtocol


class CodebaseRAG:
    """End-to-end RAG pipeline for codebase questions."""

    def __init__(
        self,
        retriever: RetrieverProtocol,
        llm: CodeLLM,
    ) -> None:
        self._retriever = retriever
        self._llm = llm

    def ask(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """Answer a question using retrieved codebase context."""

        if not query.strip():
            raise ValueError("Query must not be empty.")

        chunks = self._retriever.search(
            query=query,
            top_k=top_k,
        )

        context = ContextBuilder.build(chunks)

        prompt = f"""
You are a codebase assistant.

Answer the user's question using the provided codebase context.

Rules:
- Use only the provided context.
- Do not invent files, functions, or behavior.
- If the context does not contain enough information, say so.
- Mention relevant file paths and function/class names when useful.

Codebase context:

{context}

User question:

{query}
"""

        return self._llm.generate(prompt)