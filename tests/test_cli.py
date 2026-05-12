from pathlib import Path

from network_diagram_harness.cli import main


TMP_DIR = Path(".tmp-tests")


def test_validate_command(capsys) -> None:
    input_path = make_test_path("validate-diagram.yml")
    input_path.write_text(
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n",
        encoding="utf-8",
    )

    run_cli(["network-diagram-harness", "validate", str(input_path)])

    assert f"Valid: {input_path}" in capsys.readouterr().out


def test_preview_command_writes_markdown() -> None:
    input_path = make_test_path("preview-diagram.yml")
    output_path = make_test_path("preview.md")
    input_path.write_text(
        "title: CLI Preview\n"
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n",
        encoding="utf-8",
    )

    run_cli(
        [
            "network-diagram-harness",
            "preview",
            str(input_path),
            "--output",
            str(output_path),
        ]
    )

    assert "# CLI Preview" in output_path.read_text(encoding="utf-8")


def test_legacy_render_command_still_works(capsys) -> None:
    input_path = make_test_path("legacy-diagram.yml")
    input_path.write_text(
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n",
        encoding="utf-8",
    )

    run_cli(["network-diagram-harness", str(input_path)])

    assert 'web["Web Server"]' in capsys.readouterr().out


def test_export_command_uses_mermaid_cli(monkeypatch) -> None:
    input_path = make_test_path("export-diagram.yml")
    output_path = make_test_path("export.svg")
    input_path.write_text(
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n",
        encoding="utf-8",
    )
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.export.subprocess.run", fake_run)

    run_cli(
        [
            "network-diagram-harness",
            "export",
            str(input_path),
            "--output",
            str(output_path),
        ]
    )

    assert calls
    assert calls[0][0][0] == "mmdc"
    assert calls[0][1] is True


def test_export_all_command_uses_mermaid_cli(monkeypatch, capsys) -> None:
    input_dir = make_test_path("export-all-input")
    output_dir = make_test_path("export-all-output")
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

    run_cli(
        [
            "network-diagram-harness",
            "export-all",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "svg",
        ]
    )

    assert calls
    assert f"Exported: {output_dir / 'diagram.svg'}" in capsys.readouterr().out


def test_export_layout_command_writes_svg() -> None:
    input_path = make_test_path("layout-diagram.yml")
    output_path = make_test_path("layout.svg")
    input_path.write_text(
        "layout:\n"
        "  profile: home_lab\n"
        "nodes:\n"
        "  - id: internet\n"
        "    name: Internet\n"
        "    type: external\n",
        encoding="utf-8",
    )

    run_cli(
        [
            "network-diagram-harness",
            "export-layout",
            str(input_path),
            "--output",
            str(output_path),
        ]
    )

    content = output_path.read_text(encoding="utf-8")
    assert content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "Internet" in content


def test_cli_reports_validation_errors_without_traceback(capsys) -> None:
    input_path = make_test_path("invalid-diagram.yml")
    input_path.write_text(
        "nodes:\n"
        "  - id: web\n"
        "    name: Web Server\n"
        "    ip: 999.0.0.1\n",
        encoding="utf-8",
    )

    try:
        run_cli(["network-diagram-harness", "validate", str(input_path)])
    except SystemExit as error:
        assert error.code == 1
    else:
        raise AssertionError("Expected SystemExit")

    captured = capsys.readouterr()
    assert "error: Invalid node ip address: 999.0.0.1" in captured.err
    assert "Traceback" not in captured.err


def run_cli(argv: list[str]) -> None:
    main(argv[1:])


def make_test_path(name: str) -> Path:
    TMP_DIR.mkdir(exist_ok=True)
    return TMP_DIR / name
