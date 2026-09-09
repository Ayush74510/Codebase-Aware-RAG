# Parse command-line arguments
#         ↓
# Call index_repository()
#         ↓
# Print result

from __future__ import annotations
import argparse
from src.indexing.index_repository import index_repository


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Index a software repository into the Codebase RAG system."
    )

    parser.add_argument(
        "source",
        help="Local repository path or Git repository URL.",
    )

    args = parser.parse_args(argv)

    count = index_repository(args.source)

    print(f"Indexed {count} chunks.")


if __name__ == "__main__":
    main()