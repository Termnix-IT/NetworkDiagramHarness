from pathlib import Path

import pytest

from network_diagram_harness.export import (
    export_directory_with_mermaid_cli,
    export_with_mermaid_cli,
)
from network_diagram_harness.model import parse_diagram

TEST_DIR = Path(".tmp-tests")
TEST_DIR.mkdir(exist_ok=True)


def test_export_rejects_unsupported_format() -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})

    with pytest.raises(ValueError, match="Unsupported export format"):
        export_with_mermaid_cli(diagram, TEST_DIR / "diagram.txt")


def test_export_reports_missing_mermaid_cli(monkeypatch) -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})

    def fake_run(command, check):
        raise FileNotFoundError

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    with pytest.raises(RuntimeError, match="Mermaid CLI executable was not found"):
        export_with_mermaid_cli(diagram, TEST_DIR / "diagram.svg")


def test_export_directory_exports_each_yaml(monkeypatch) -> None:
    input_dir = TEST_DIR / "export-all-input"
    output_dir = TEST_DIR / "export-all-output"
    if input_dir.exists():
        for path in input_dir.glob("*.yml"):
            path.unlink()
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "one.yml").write_text(
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n",
        encoding="utf-8",
    )
    (input_dir / "two.yml").write_text(
        "nodes:\n"
        "  - id: db\n"
        "    name: Database\n"
        "    type: database\n",
        encoding="utf-8",
    )
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    output_paths = export_directory_with_mermaid_cli(input_dir, output_dir)

    assert output_paths == [output_dir / "one.svg", output_dir / "two.svg"]
    assert len(calls) == 2
