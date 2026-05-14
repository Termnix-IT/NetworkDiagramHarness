from __future__ import annotations

from html import escape
import json

from network_diagram_harness.model import Connection, Diagram, Node
from network_diagram_harness.renderers.styles import node_style_profile


class PyvisRenderer:
    name = "pyvis"
    source_suffix = ".html"

    def render_source(self, diagram: Diagram) -> str:
        return render_pyvis_html(diagram)


def render_pyvis_html(diagram: Diagram) -> str:
    nodes = [render_node(diagram, node) for node in diagram.nodes]
    edges = [render_edge(connection) for connection in diagram.connections]
    title = diagram.title or "Network Diagram"

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)}</title>",
            '<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>',
            "<style>",
            "html, body { height: 100%; margin: 0; font-family: Arial, sans-serif; }",
            "body { background: #f8fafc; color: #111827; }",
            "#network { width: 100vw; height: 100vh; }",
            ".vis-tooltip { font-family: Arial, sans-serif; }",
            "</style>",
            "</head>",
            "<body>",
            '<div id="network"></div>',
            "<script>",
            f"const nodes = new vis.DataSet({json.dumps(nodes, ensure_ascii=False)});",
            f"const edges = new vis.DataSet({json.dumps(edges, ensure_ascii=False)});",
            "const container = document.getElementById('network');",
            "const data = { nodes, edges };",
            "const options = {",
            "  layout: { improvedLayout: true },",
            "  physics: { solver: 'forceAtlas2Based', stabilization: { iterations: 180 } },",
            "  interaction: { hover: true, navigationButtons: true, keyboard: true },",
            "  nodes: { borderWidth: 1.5, shape: 'box', margin: 10, font: { face: 'Arial', size: 14 } },",
            "  edges: { color: '#475569', arrows: { to: { enabled: true, scaleFactor: 0.8 } }, font: { face: 'Arial', size: 11, align: 'middle' }, smooth: { type: 'dynamic' } },",
            "};",
            "new vis.Network(container, data, options);",
            "</script>",
            "</body>",
            "</html>",
            "",
        ]
    )


def render_node(diagram: Diagram, node: Node) -> dict[str, object]:
    style = node_style_profile(diagram.style.profile)[node.type]
    label = node.name
    detail = " / ".join(value for value in [node.ip, node.role] if value)
    if detail:
        label = f"{label}\n{detail}"
    value: dict[str, object] = {
        "id": node.id,
        "label": label,
        "group": node.group or node.type,
        "color": {"background": style["fillcolor"], "border": style["color"]},
        "title": node.description or node.role or node.type,
    }
    if node.order is not None:
        value["level"] = node.order
    return value


def render_edge(connection: Connection) -> dict[str, object]:
    source = connection.source
    target = connection.target
    arrows = "to"
    if connection.direction == "inbound":
        source, target = target, source
    elif connection.direction == "bidirectional":
        arrows = "to, from"

    value: dict[str, object] = {
        "from": source,
        "to": target,
        "arrows": arrows,
    }
    label = connection_label(connection)
    if label:
        value["label"] = label
    return value


def connection_label(connection: Connection) -> str:
    if connection.label:
        return connection.label
    parts = []
    if connection.protocol:
        parts.append(connection.protocol)
    if connection.port:
        parts.append(str(connection.port))
    if connection.purpose:
        parts.append(connection.purpose)
    return " / ".join(parts)
