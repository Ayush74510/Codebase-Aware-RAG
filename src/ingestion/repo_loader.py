from __future__ import annotations
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from git import Repo # type: ignore


# Files that are generally not useful for codebase RAG
IGNORED_DIRS = {
    ".git",
    ".github",
    ".gitlab",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    "target",
    "coverage",
}

# Start with common source/config/documentation files.
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cc",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".kts",
    ".scala",
    ".cs",
    ".sql",
    ".sh",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".xml",
    ".md",
    ".txt",
}


@dataclass
class RepositoryFile:
    """Represents a file extracted from a repository."""

    path: str
    absolute_path: Path
    content: str
    language: str | None
    size_bytes: int


class RepositoryLoader:
    """
    Load files from a local Git repository or clone a remote repository.

    Responsibilities:
    - Clone remote repositories
    - Walk repository files
    - Filter irrelevant files/directories
    - Read text files
    - Return structured RepositoryFile objects

    This class does NOT:
    - chunk code
    - generate embeddings
    - store vectors
    - perform retrieval
    """

    def __init__(self,max_file_size_mb: int = 2) -> None:
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self._temporary_directories: list[Path] = []

    def load(self, source: str) -> list[RepositoryFile]:
        """
        Load files from either:

        1. A local repository path
        2. A remote Git repository URL

        Example:
            loader.load("./my-project")
            loader.load("https://github.com/user/project.git")
        """

        source_path = Path(source)

        if source_path.exists():
            repo_path = source_path.resolve()
            should_cleanup = False
            
        elif self._is_git_url(source):
            repo_path = self._clone_repository(source)
            should_cleanup = True
            
        else:
            raise FileNotFoundError(f"Repository source does not exist or is not a valid Git URL: {source}")

        try:
            return self._walk_repository(repo_path)
        finally:
            if should_cleanup:
                self._cleanup_repository(repo_path)

    def _clone_repository(self, url: str) -> Path:
        """Clone a remote Git repository into a temporary directory."""

        temp_dir = Path(tempfile.mkdtemp(prefix="codebase_rag_"))
        self._temporary_directories.append(temp_dir)

        try:
            Repo.clone_from(
                url,
                temp_dir,
                depth=1,
            )
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

        return temp_dir

    def _walk_repository(self, repo_path: Path) -> list[RepositoryFile]:
        """Walk the repository and collect supported files."""

        files: list[RepositoryFile] = []

        for path in repo_path.rglob("*"):
            if not path.is_file():
                continue

            if self._should_ignore(path, repo_path):
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            if path.stat().st_size > self.max_file_size:
                continue

            repository_file = self._read_file(path, repo_path)

            if repository_file is not None:
                files.append(repository_file)

        return files

    def _read_file(self,path: Path,repo_path: Path) -> RepositoryFile | None:
        """Read a repository file as UTF-8 text."""

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except (OSError, UnicodeError):
            return None

        relative_path = path.relative_to(repo_path)

        return RepositoryFile(
            path=relative_path.as_posix(),
            absolute_path=path,
            content=content,
            language=self._detect_language(path),
            size_bytes=path.stat().st_size,
        )

    @staticmethod
    def _should_ignore(path: Path,repo_path: Path) -> bool:
        """Determine whether a file belongs to an ignored directory."""

        relative_path = path.relative_to(repo_path)

        return any(
            part in IGNORED_DIRS
            for part in relative_path.parts
        )

    @staticmethod
    def _detect_language(path: Path) -> str | None:
        """Map file extensions to programming languages."""

        extension_to_language = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".hpp": "cpp",
            ".cc": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".kts": "kotlin",
            ".scala": "scala",
            ".cs": "csharp",
            ".sql": "sql",
            ".sh": "shell",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".toml": "toml",
            ".xml": "xml",
            ".md": "markdown",
            ".txt": "text",
        }

        return extension_to_language.get(path.suffix.lower())

    @staticmethod
    def _is_git_url(source: str) -> bool:
        """Return True if source looks like a Git repository URL."""

        parsed = urlparse(source)

        return parsed.scheme in {"http", "https", "ssh", "git"}

    @staticmethod
    def _cleanup_repository(repo_path: Path) -> None:
        """Remove a temporary cloned repository."""

        shutil.rmtree(repo_path, ignore_errors=True)