from pathlib import Path

from network_diagram_harness.model import parse_diagram
from network_diagram_harness.svg import render_layout_svg, write_layout_svg


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
