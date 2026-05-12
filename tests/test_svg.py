from pathlib import Path

from network_diagram_harness.model import parse_diagram
from network_diagram_harness.svg import export_layout, render_layout_svg, write_layout_svg


def test_render_home_lab_svg_layout() -> None:
    diagram = parse_diagram(
        {
            "title": "Profile Home Lab Network",
            "layout": {"profile": "home_lab"},
            "zones": [
                {"id": "internet", "name": "Internet"},
                {"id": "cloud", "name": "Cloud Hosting"},
                {"id": "internal", "name": "Segmented Internal Network"},
            ],
            "nodes": [
                {
                    "id": "internet",
                    "name": "Internet",
                    "type": "external",
                    "zone": "internet",
                },
                {
                    "id": "cdn",
                    "name": "CDN",
                    "type": "load_balancer",
                    "zone": "cloud",
                },
                {
                    "id": "internal_router",
                    "name": "Internal Router",
                    "type": "firewall",
                    "zone": "internal",
                },
            ],
            "connections": [
                {"source": "internet", "target": "cdn", "protocol": "HTTPS", "port": 443},
                {"source": "internet", "target": "internal_router", "label": "WAN"},
            ],
        }
    )

    output = render_layout_svg(diagram)

    assert output.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<svg" in output
    assert "Profile Home Lab Network" in output
    assert "Cloud Hosting" in output
    assert "Internal Router" in output
    assert "HTTPS / 443" in output


def test_layout_svg_requires_home_lab_profile() -> None:
    diagram = parse_diagram({"nodes": [{"id": "web", "name": "Web Server"}]})

    try:
        render_layout_svg(diagram)
    except ValueError as error:
        assert "layout.profile: home_lab" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_write_layout_svg_rejects_non_svg_output() -> None:
    diagram = parse_diagram(
        {
            "layout": {"profile": "home_lab"},
            "nodes": [{"id": "web", "name": "Web Server"}],
        }
    )

    try:
        write_layout_svg(diagram, Path(".tmp-tests/layout.png"))
    except ValueError as error:
        assert ".svg output only" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_export_layout_accepts_svg_output() -> None:
    diagram = parse_diagram(
        {
            "layout": {"profile": "home_lab"},
            "nodes": [{"id": "internet", "name": "Internet", "type": "external"}],
        }
    )
    output_path = Path(".tmp-tests/layout.svg")

    export_layout(diagram, output_path)

    assert output_path.read_text(encoding="utf-8").startswith(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )


def test_export_layout_png_uses_node_helper(monkeypatch) -> None:
    diagram = parse_diagram(
        {
            "layout": {"profile": "home_lab"},
            "nodes": [{"id": "internet", "name": "Internet", "type": "external"}],
        }
    )
    calls = []

    def fake_run(command, check):
        calls.append((command, check))

    monkeypatch.setattr("network_diagram_harness.svg.subprocess.run", fake_run)

    export_layout(
        diagram,
        Path(".tmp-tests/layout.png"),
        puppeteer_config_file=Path("scripts/puppeteer-config.json"),
    )

    command, check = calls[0]
    assert check is True
    assert command[0] == "node"
    assert "svg-to-png.mjs" in command[1]
    assert "--puppeteer-config-file" in command


def test_export_layout_rejects_unsupported_output() -> None:
    diagram = parse_diagram(
        {
            "layout": {"profile": "home_lab"},
            "nodes": [{"id": "internet", "name": "Internet", "type": "external"}],
        }
    )

    try:
        export_layout(diagram, Path(".tmp-tests/layout.pdf"))
    except ValueError as error:
        assert ".svg and .png output" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_unknown_layout_profile_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "layout": {"profile": "rack"},
                "nodes": [{"id": "web", "name": "Web Server"}],
            }
        )
    except ValueError as error:
        assert "Unsupported layout profile: rack" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_render_home_lab_private_uses_larger_canvas() -> None:
    diagram = parse_diagram(
        {
            "title": "Private Home Lab",
            "layout": {"profile": "home_lab_private"},
            "zones": [{"id": "internet", "name": "Internet"}],
            "nodes": [
                {
                    "id": "internet",
                    "name": "Internet",
                    "type": "external",
                    "zone": "internet",
                    "role": "Long provider detail / dynamic DNS",
                }
            ],
        }
    )

    output = render_layout_svg(diagram)

    assert 'width="1700"' in output
    assert 'height="1100"' in output
    assert "Long provider detail" in output
