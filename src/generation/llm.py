from __future__ import annotations
import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class CodeLLM:
    """Generate responses using the configured LLM."""

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
            "LLM_MODEL",
            "gemini-2.5-flash",
        )

    def generate(self, prompt: str) -> str:
        """Generate a response from a prompt."""

        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("LLM returned an empty response.")

        return content