from pathlib import Path
from src.ingestion.ast_chunker import ASTChunker
from src.ingestion.repo_loader import RepositoryFile


def test_python_functions_are_chunked():
    content = """
def hello(name):
    return f"Hello {name}"


def add(a, b):
    return a + b
""".strip()

    repository_file = RepositoryFile(
        path="example.py",
        absolute_path=None,
        content=content,
        language="python",
        size_bytes=len(content.encode("utf-8")),
    )

    chunker = ASTChunker()

    chunks = chunker.chunk(repository_file)

    assert len(chunks) == 2

    assert chunks[0].name == "hello"
    assert chunks[0].chunk_type == "function"

    assert chunks[1].name == "add"
    assert chunks[1].chunk_type == "function"


def test_python_class_is_chunked():
    content = """
class Calculator:

    def add(self, a, b):
        return a + b
""".strip()

    repository_file = RepositoryFile(
        path="calculator.py",
        absolute_path=None,
        content=content,
        language="python",
        size_bytes=len(content.encode("utf-8")),
    )

    chunker = ASTChunker()

    chunks = chunker.chunk(repository_file)

    assert any(
        chunk.name == "Calculator"
        and chunk.chunk_type == "class"
        for chunk in chunks
    )


def test_unsupported_language_uses_fallback():
    content = "some unknown source code"

    repository_file = RepositoryFile(
        path="example.xyz",
        absolute_path=None,
        content=content,
        language="xyz",
        size_bytes=len(content.encode("utf-8")),
    )

    chunker = ASTChunker()

    chunks = chunker.chunk(repository_file)

    assert len(chunks) == 1
    assert chunks[0].chunk_type == "file"
    assert chunks[0].content == content
    
def test_methods_are_distinguished_from_functions():
    content = """
class Calculator:

    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


def divide(a, b):
    return a / b
""".strip()

    repository_file = RepositoryFile(
        path="calculator.py",
        absolute_path=Path("calculator.py"),
        content=content,
        language="python",
        size_bytes=len(content.encode("utf-8")),
    )

    chunker = ASTChunker()

    chunks = chunker.chunk(repository_file)

    calculator = next(
        chunk
        for chunk in chunks
        if chunk.name == "Calculator"
    )

    add = next(
        chunk
        for chunk in chunks
        if chunk.name == "add"
    )

    multiply = next(
        chunk
        for chunk in chunks
        if chunk.name == "multiply"
    )

    divide = next(
        chunk
        for chunk in chunks
        if chunk.name == "divide"
    )

    assert calculator.chunk_type == "class"

    assert add.chunk_type == "method"
    assert add.metadata.parent_class == "Calculator"

    assert multiply.chunk_type == "method"
    assert multiply.metadata.parent_class == "Calculator"

    assert divide.chunk_type == "function"
    assert divide.metadata.parent_class is None
    
def test_metadata_is_extracted():
    content = """
class Calculator:

    @staticmethod
    def add(a, b):
        return a + b
""".strip()

    repository_file = RepositoryFile(
        path="calculator.py",
        absolute_path=Path("calculator.py"),
        content=content,
        language="python",
        size_bytes=len(content.encode("utf-8")),
    )

    chunker = ASTChunker()

    chunks = chunker.chunk(repository_file)

    add = next(
        chunk
        for chunk in chunks
        if chunk.name == "add"
    )

    assert add.chunk_type == "method"
    assert add.metadata.parent_class == "Calculator"
    assert "@staticmethod" in add.metadata.decorators