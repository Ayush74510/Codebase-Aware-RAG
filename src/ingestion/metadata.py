from __future__ import annotations
from dataclasses import dataclass, field
from tree_sitter import Node  # type: ignore


@dataclass
class ChunkMetadata:
    """Metadata that improves code retrieval and understanding."""

    parent_class: str | None = None
    parent_function: str | None = None
    decorators: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)


class MetadataExtractor:
    """Extract relevant metadata from a Tree-sitter syntax tree."""

    def extract(
        self,
        node: Node,
        source_bytes: bytes,
        parent_class: str | None = None,
        parent_function: str | None = None,
    ) -> ChunkMetadata:
        """Extract metadata relevant to a single code chunk."""

        metadata = ChunkMetadata(
            parent_class=parent_class,
            parent_function=parent_function,
        )

        self._extract_decorators(
            node=node,
            source_bytes=source_bytes,
            metadata=metadata,
        )

        self._extract_calls(
            node=node,
            source_bytes=source_bytes,
            metadata=metadata,
        )

        self._extract_imports(
            node=node,
            source_bytes=source_bytes,
            metadata=metadata,
        )

        return metadata

    def _extract_decorators(
        self,
        node: Node,
        source_bytes: bytes,
        metadata: ChunkMetadata,
    ) -> None:
        """Extract decorators attached to a function or class."""

        # If the node itself is a decorated_definition,
        # inspect its decorator children.
        if node.type == "decorated_definition":
            for child in node.children:
                if child.type == "decorator":
                    decorator = self._node_text(
                        child,
                        source_bytes,
                    )

                    if decorator not in metadata.decorators:
                        metadata.decorators.append(decorator)

            return

        # When extracting metadata from the actual
        # function/class node, its parent may be
        # decorated_definition.
        parent = node.parent

        if parent is None or parent.type != "decorated_definition":
            return

        for child in parent.children:
            if child.type != "decorator":
                continue

            decorator = self._node_text(
                child,
                source_bytes,
            )

            if decorator not in metadata.decorators:
                metadata.decorators.append(decorator)

    def _extract_calls(
        self,
        node: Node,
        source_bytes: bytes,
        metadata: ChunkMetadata,
    ) -> None:
        """Extract directly referenced function/method calls."""

        self._walk_calls(
            node=node,
            source_bytes=source_bytes,
            metadata=metadata,
        )

    def _walk_calls(
        self,
        node: Node,
        source_bytes: bytes,
        metadata: ChunkMetadata,
    ) -> None:
        """
        Recursively find call expressions.

        Nested function/class definitions are skipped so that
        calls belonging to another semantic chunk are not mixed
        into the current chunk.
        """

        if node is not None and node.type == "call":
            function_node = node.child_by_field_name("function")

            if function_node is not None:
                call_name = self._node_text(
                    function_node,
                    source_bytes,
                )

                if call_name and call_name not in metadata.calls:
                    metadata.calls.append(call_name)

            return

        for child in node.children:
            if child.type in {
                "function_definition",
                "class_definition",
            }:
                continue

            self._walk_calls(
                node=child,
                source_bytes=source_bytes,
                metadata=metadata,
            )

    def _extract_imports(
        self,
        node: Node,
        source_bytes: bytes,
        metadata: ChunkMetadata,
    ) -> None:
        """
        Extract imports that occur inside the current chunk.

        Module-level imports are handled separately later.
        """

        self._walk_imports(
            node=node,
            source_bytes=source_bytes,
            metadata=metadata,
        )

    def _walk_imports(
        self,
        node: Node,
        source_bytes: bytes,
        metadata: ChunkMetadata,
    ) -> None:
        """Find import statements within the current node."""

        if node.type in {
            "import_statement",
            "import_from_statement",
        }:
            import_text = self._node_text(
                node,
                source_bytes,
            )

            if import_text not in metadata.imports:
                metadata.imports.append(import_text)

            return

        for child in node.children:
            if child.type in {
                "function_definition",
                "class_definition",
            }:
                continue

            self._walk_imports(
                node=child,
                source_bytes=source_bytes,
                metadata=metadata,
            )

    @staticmethod
    def _node_text(
        node: Node,
        source_bytes: bytes,
    ) -> str:
        """Convert an AST node into source text."""

        return (
            source_bytes[node.start_byte : node.end_byte]
            .decode(
                "utf-8",
                errors="ignore",
            )
            .strip()
        )
