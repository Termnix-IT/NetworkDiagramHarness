from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_prompt_workflow_docs_exist() -> None:
    assert (ROOT / "docs" / "prompt-workflow.md").exists()
    assert (ROOT / "prompts" / "network-diagram-request.md").exists()


def test_public_docs_do_not_contain_local_absolute_paths() -> None:
    paths = [
        *ROOT.glob("README.md"),
        *ROOT.glob("docs/**/*.md"),
        *ROOT.glob("prompts/**/*.md"),
        *ROOT.glob("examples/*.yml"),
    ]
    forbidden = ["C:/Users/", "C:\\Users\\", "ProjectFolder", "lugep"]

    for path in paths:
        content = path.read_text(encoding="utf-8")
        for value in forbidden:
            assert value not in content, f"{path} contains local path fragment: {value}"
