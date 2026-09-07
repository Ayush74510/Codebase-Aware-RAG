# → responsible ONLY for talking to FreeLLMAPI

from __future__ import annotations
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()


class CodeEmbedder:
    """Generate embeddings for source code using FreeLLMAPI."""

    def __init__(self) -> None:
        api_key = os.getenv("FREELLMAPI_API_KEY")
        base_url = os.getenv(
            "FREELLMAPI_BASE_URL",
            "http://127.0.0.1:31415/v1",
        )

        if not api_key:
            raise RuntimeError(
                "FREELLMAPI_API_KEY environment variable is not set."
            )

        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self._model = os.getenv(
            "EMBEDDING_MODEL",
            "bge-m3",
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple code chunks."""

        if not texts:
            return []

        response = self._client.embeddings.create(
            model=self._model,
            input=texts,
        )

        return [item.embedding for item in response.data]
    
    def embed_query(self, query: str) -> list[float]:
        """Generate an embedding for a search query."""

        if not query.strip():
            raise ValueError("Query must not be empty.")

        return self.embed_documents([query])[0]