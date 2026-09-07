from __future__ import annotations
from dataclasses import dataclass
import tree_sitter_python as tspython  # type: ignore
from tree_sitter import Language, Node, Parser  # type: ignore
from .repo_loader import RepositoryFile
from .metadata import ChunkMetadata, MetadataExtractor

PYTHON_LANGUAGE = Language(tspython.language())


@dataclass
class CodeChunk:
    """Represents a semantically meaningful piece of source code."""

    file_path: str
    chunk_type: str
    name: str
    content: str
    start_line: int
    end_line: int
    language: str
    metadata: ChunkMetadata


class ASTChunker:
    """
    Parse source files using Tree-sitter and extract semantic code chunks.

    Currently supports Python.

    Extracted chunk types:
        - class
        - function
        - method

    Unsupported languages fall back to one file-level chunk.
    """

    def __init__(self) -> None:
        self._parsers = {
            "python": Parser(PYTHON_LANGUAGE),
        }

        self._metadata_extractor = MetadataExtractor()

    def chunk(self, repository_file: RepositoryFile) -> list[CodeChunk]:
        """Convert a RepositoryFile into semantic code chunks."""

        parser = self._parsers.get(repository_file.language)

        if parser is None:
            return self._fallback_chunk(repository_file)

        source_bytes = repository_file.content.encode("utf-8")

        tree = parser.parse(source_bytes)

        return self._extract_python_chunks(
            root=tree.root_node,
            source_bytes=source_bytes,
            repository_file=repository_file,
        )

    def _extract_python_chunks(
        self,
        root: Node,
        source_bytes: bytes,
        repository_file: RepositoryFile,
    ) -> list[CodeChunk]:
        """Extract classes, functions, and methods."""

        chunks: list[CodeChunk] = []

        self._walk_python_tree(
            node=root,
            source_bytes=source_bytes,
            repository_file=repository_file,
            chunks=chunks,
            parent_class=None,
            parent_function=None,
        )

        return chunks

    def _walk_python_tree(
        self,
        node: Node,
        source_bytes: bytes,
        repository_file: RepositoryFile,
        chunks: list[CodeChunk],
        parent_class: str | None,
        parent_function: str | None = None,
    ) -> None:
        """Recursively walk the Python AST."""

        current_parent_class = parent_class
        current_parent_function = parent_function

        if node.type == "class_definition":
            class_name = self._get_node_name(
                node=node,
                source_bytes=source_bytes,
            )

            chunks.append(
                self._create_chunk(
                    node=node,
                    chunk_type="class",
                    source_bytes=source_bytes,
                    repository_file=repository_file,
                    parent_class=parent_class,
                    parent_function=parent_function,
                )
            )

            current_parent_class = class_name
            current_parent_function = None

        elif node.type == "function_definition":
            function_name = self._get_node_name(
                node=node,
                source_bytes=source_bytes,
            )

            chunk_type = "method" if parent_class is not None else "function"

            chunks.append(
                self._create_chunk(
                    node=node,
                    chunk_type=chunk_type,
                    source_bytes=source_bytes,
                    repository_file=repository_file,
                    parent_class=parent_class,
                    parent_function=parent_function,
                )
            )

            current_parent_function = function_name

        for child in node.children:
            self._walk_python_tree(
                node=child,
                source_bytes=source_bytes,
                repository_file=repository_file,
                chunks=chunks,
                parent_class=current_parent_class,
                parent_function=current_parent_function,
            )

    def _create_chunk(
        self,
        node: Node,
        chunk_type: str,
        source_bytes: bytes,
        repository_file: RepositoryFile,
        parent_class: str | None,
        parent_function: str | None = None,
    ) -> CodeChunk:
        """Create a CodeChunk from an AST node."""

        content = source_bytes[node.start_byte : node.end_byte].decode(
            "utf-8",
            errors="ignore",
        )

        name = self._get_node_name(
            node=node,
            source_bytes=source_bytes,
        )

        metadata = self._metadata_extractor.extract(
            node=node,
            source_bytes=source_bytes,
            parent_class=parent_class,
            parent_function=parent_function,
        )

        return CodeChunk(
            file_path=repository_file.path,
            chunk_type=chunk_type,
            name=name,
            content=content,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            language=repository_file.language or "unknown",
            metadata=metadata,
        )

    @staticmethod
    def _get_node_name(
        node: Node,
        source_bytes: bytes,
    ) -> str:
        """Extract the name of a class or function."""

        name_node = node.child_by_field_name("name")

        if name_node is None:
            return "<anonymous>"

        return source_bytes[name_node.start_byte : name_node.end_byte].decode(
            "utf-8",
            errors="ignore",
        )

    @staticmethod
    def _fallback_chunk(
        repository_file: RepositoryFile,
    ) -> list[CodeChunk]:
        """Return the complete file as one chunk."""

        line_count = (
            repository_file.content.count("\n") + 1 if repository_file.content else 0
        )

        return [
            CodeChunk(
                file_path=repository_file.path,
                chunk_type="file",
                name=repository_file.path,
                content=repository_file.content,
                start_line=1,
                end_line=line_count,
                language=repository_file.language or "unknown",
                metadata=ChunkMetadata(),
            )
        ]
