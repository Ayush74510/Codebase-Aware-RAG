from scripts.index_repo import main


def test_index_repo_cli(capsys, monkeypatch):
    def fake_index_repository(source: str) -> int:
        assert source == "test-repository"
        return 42

    monkeypatch.setattr(
        "scripts.index_repo.index_repository",
        fake_index_repository,
    )

    main(["test-repository"])

    captured = capsys.readouterr()

    assert "Indexed 42 chunks." in captured.out