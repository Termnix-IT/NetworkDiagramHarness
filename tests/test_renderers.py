from network_diagram_harness.model import parse_diagram
from network_diagram_harness.renderers.drawsvg import build_layout
from network_diagram_harness.renderers.drawsvg import render_drawsvg_svg
from network_diagram_harness.renderers.pyvis import render_pyvis_html


def test_links_alias_is_parsed_as_connections() -> None:
    diagram = parse_diagram(
        {
            "nodes": [
                {"id": "internet", "name": "Internet", "type": "external"},
                {"id": "web", "name": "Web Server", "type": "server"},
            ],
            "links": [
                {"source": "internet", "target": "web", "label": "HTTPS"},
            ],
        }
    )

    assert len(diagram.connections) == 1
    assert diagram.connections[0].source == "internet"
    assert diagram.connections[0].target == "web"


def test_unknown_style_profile_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "style": {"profile": "unknown"},
                "nodes": [{"id": "web", "name": "Web Server"}],
            }
        )
    except ValueError as error:
        assert "Unsupported style profile: unknown" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_node_order_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [{"id": "web", "name": "Web Server", "order": "first"}],
            }
        )
    except ValueError as error:
        assert "Invalid node order: first" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_unknown_node_rank_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [{"id": "web", "name": "Web Server", "rank": "middle"}],
            }
        )
    except ValueError as error:
        assert "Unsupported node rank: middle" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_drawsvg_renderer_outputs_svg() -> None:
    diagram = parse_diagram(
        {
            "title": "Drawsvg Network",
            "zones": [{"id": "dmz", "name": "DMZ"}],
            "nodes": [{"id": "web", "name": "Web Server", "zone": "dmz"}],
        }
    )

    output = render_drawsvg_svg(diagram)

    assert output.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert "<svg " in output
    assert "Drawsvg Network" in output
    assert "Web Server" in output


def test_drawsvg_renderer_expands_width_for_many_zones() -> None:
    diagram = parse_diagram(
        {
            "zones": [{"id": f"zone{i}", "name": f"Zone {i}"} for i in range(6)],
            "nodes": [
                {"id": f"node{i}", "name": f"Node {i}", "zone": f"zone{i}"}
                for i in range(6)
            ],
        }
    )

    output = render_drawsvg_svg(diagram)
    zone_boxes, node_boxes = build_layout(diagram)
    right_edge = max(
        [box.x + box.width for box in zone_boxes.values()]
        + [box.x + box.width for box in node_boxes.values()]
    )

    width_marker = '<svg xmlns="http://www.w3.org/2000/svg" width="'
    width_start = output.index(width_marker) + len(width_marker)
    width_end = output.index('"', width_start)
    width = int(output[width_start:width_end])

    assert width > 1400
    assert width > right_edge


def test_pyvis_renderer_outputs_html() -> None:
    diagram = parse_diagram(
        {
            "title": "Pyvis Network",
            "nodes": [
                {"id": "internet", "name": "Internet", "type": "external"},
                {"id": "web", "name": "Web Server", "type": "server"},
            ],
            "connections": [{"source": "internet", "target": "web", "label": "HTTPS"}],
        }
    )

    output = render_pyvis_html(diagram)

    assert output.startswith("<!doctype html>")
    assert "vis-network" in output
    assert "Pyvis Network" in output
    assert '"label": "HTTPS"' in output
