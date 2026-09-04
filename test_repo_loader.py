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


if __name__ == "__main__":
    main()