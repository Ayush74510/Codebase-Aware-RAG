from src.generation.llm import CodeLLM


llm = CodeLLM()

response = llm.generate(
    "Explain what this Python function does:\n\n"
    "def add(a, b):\n"
    "    return a + b"
)

print(response)