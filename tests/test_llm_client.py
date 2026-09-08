from src.generation.llm import CodeLLM


def test_llm_generates_response():
    llm = CodeLLM()

    response = llm.generate(
        "Explain what this Python function does:\n\n"
        "def add(a, b):\n"
        "    return a + b"
    )

    assert response
    assert "add" in response.lower()