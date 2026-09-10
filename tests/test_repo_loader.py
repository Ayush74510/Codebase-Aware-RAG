from src.ingestion.repo_loader import RepositoryLoader


def main():
    loader = RepositoryLoader()

    files = loader.load("./test_repo")

    print(f"Files found: {len(files)}")
    print()

    for file in files:
        print("=" * 60)
        print(f"FILE: {file.path}")
        print(f"LANGUAGE: {file.language}")
        print()
        print(file.content)
        
def test_loader_can_ignore_additional_directories(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    src_dir = repo_dir / "src"
    tests_dir = repo_dir / "tests"

    src_dir.mkdir()
    tests_dir.mkdir()

    (src_dir / "main.py").write_text(
        "def main():\n    return 1\n",
        encoding="utf-8",
    )

    (tests_dir / "test_main.py").write_text(
        "def test_main():\n    assert True\n",
        encoding="utf-8",
    )

    loader = RepositoryLoader(ignored_dirs={"tests"})
    files = loader.load(str(repo_dir))

    paths = {file.path for file in files}

    assert "src/main.py" in paths
    assert "tests/test_main.py" not in paths


if __name__ == "__main__":
    main()