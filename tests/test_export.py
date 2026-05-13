from pathlib import Path

import pytest

from network_diagram_harness.export import (
    export_diagram,
    export_directory,
    export_directory_with_graphviz,
    export_directory_with_mermaid_cli,
    export_with_graphviz,
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


def test_export_passes_puppeteer_config_file(monkeypatch) -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    export_with_mermaid_cli(
        diagram,
        TEST_DIR / "diagram.png",
        puppeteer_config_file=Path("scripts/puppeteer-config.json"),
        width=1400,
        height=1000,
    )

    command, check = calls[0]
    assert check is True
    assert "--puppeteerConfigFile" in command
    assert "scripts\\puppeteer-config.json" in command or "scripts/puppeteer-config.json" in command
    assert "--width" in command
    assert "1400" in command
    assert "--height" in command
    assert "1000" in command


def test_export_diagram_dispatches_to_graphviz(monkeypatch) -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    export_diagram(
        diagram,
        TEST_DIR / "dispatch.svg",
        renderer="graphviz",
        dot_command="dot",
    )

    assert calls
    assert calls[0][0][0] == "dot"


def test_export_diagram_rejects_unknown_renderer() -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})

    with pytest.raises(ValueError, match="Unsupported export renderer"):
        export_diagram(diagram, TEST_DIR / "dispatch.svg", renderer="unknown")


def test_graphviz_export_rejects_unsupported_format() -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})

    with pytest.raises(ValueError, match="Unsupported Graphviz export format"):
        export_with_graphviz(diagram, TEST_DIR / "diagram.txt")


def test_graphviz_export_reports_missing_dot(monkeypatch) -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})

    def fake_run(command, check):
        raise FileNotFoundError

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    with pytest.raises(RuntimeError, match="Graphviz dot executable was not found"):
        export_with_graphviz(diagram, TEST_DIR / "diagram.svg")


def test_graphviz_export_invokes_dot(monkeypatch) -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    export_with_graphviz(diagram, TEST_DIR / "diagram.png", dot_command="dot")

    command, check = calls[0]
    assert check is True
    assert command[0] == "dot"
    assert "-Tpng" in command
    assert "-o" in command
    assert str(TEST_DIR / "diagram.png") in command


def test_graphviz_export_directory_exports_each_yaml(monkeypatch) -> None:
    input_dir = TEST_DIR / "graphviz-export-all-input"
    output_dir = TEST_DIR / "graphviz-export-all-output"
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

    output_paths = export_directory_with_graphviz(input_dir, output_dir)

    assert output_paths == [output_dir / "one.svg", output_dir / "two.svg"]
    assert len(calls) == 2


def test_export_directory_dispatches_to_graphviz(monkeypatch) -> None:
    input_dir = TEST_DIR / "dispatch-export-all-input"
    output_dir = TEST_DIR / "dispatch-export-all-output"
    if input_dir.exists():
        for path in input_dir.glob("*.yml"):
            path.unlink()
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "diagram.yml").write_text(
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n",
        encoding="utf-8",
    )
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    output_paths = export_directory(
        input_dir,
        output_dir,
        renderer="graphviz",
        image_format="png",
    )

    assert output_paths == [output_dir / "diagram.png"]
    assert calls[0][0][0] == "dot"
