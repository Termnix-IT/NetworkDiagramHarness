from __future__ import annotations

import re

from .model import Connection, Diagram, Node


NODE_STYLES = {
    "external": "([{}])",
    "firewall": "{{{}}}",
    "load_balancer": "([{}])",
    "database": "[({})]",
    "network": "[/{} /]",
    "subnet": "[{}]",
    "server": "[{}]",
}

NODE_CLASS_STYLES = {
    "database": "fill:#fef3c7,stroke:#b45309,color:#111827",
    "external": "fill:#e0f2fe,stroke:#0369a1,color:#111827",
    "firewall": "fill:#fee2e2,stroke:#b91c1c,color:#111827",
    "load_balancer": "fill:#dcfce7,stroke:#15803d,color:#111827",
    "network": "fill:#f1f5f9,stroke:#475569,color:#111827",
    "server": "fill:#ede9fe,stroke:#6d28d9,color:#111827",
    "subnet": "fill:#ecfeff,stroke:#0e7490,color:#111827",
}


def render_mermaid(diagram: Diagram) -> str:
    lines = [f"flowchart {diagram.direction}"]

    if diagram.title:
        lines.append(f"  %% {escape_comment(diagram.title)}")

    rendered_nodes = set()
    nodes_by_zone = {
        zone.id: [node for node in diagram.nodes if node.zone == zone.id]
        for zone in diagram.zones
    }

    for zone in diagram.zones:
        zone_nodes = nodes_by_zone[zone.id]
        if not zone_nodes:
            continue

        zone_graph_id = sanitize_zone_id(zone.id)
        lines.append(f"  subgraph {zone_graph_id}[\"{escape_label(zone.name)}\"]")
        for node in zone_nodes:
            lines.append(f"    {sanitize_id(node.id)}{render_node_shape(node)}")
            rendered_nodes.add(node.id)
        lines.append("  end")

    for node in diagram.nodes:
        if node.id not in rendered_nodes:
            lines.append(f"  {sanitize_id(node.id)}{render_node_shape(node)}")

    for connection in diagram.connections:
        source = sanitize_id(connection.source)
        target = sanitize_id(connection.target)
        label = render_connection_label(connection)
        arrow = render_connection_arrow(connection)
        if label:
            lines.append(f"  {source} {arrow}|\"{escape_label(label)}\"| {target}")
        else:
            lines.append(f"  {source} {arrow} {target}")

    append_node_classes(lines, diagram.nodes)

    return "\n".join(lines) + "\n"


def render_node_shape(node: Node) -> str:
    label = escape_label(render_node_label(node))
    shape = NODE_STYLES.get(node.type, NODE_STYLES["server"])
    return shape.format(f'"{label}"')


def render_node_label(node: Node) -> str:
    details = [value for value in [node.ip, node.role] if value]
    if not details:
        return node.name
    return f"{node.name}<br/>{' / '.join(details)}"


def render_connection_label(connection: Connection) -> str | None:
    if connection.label:
        return connection.label

    parts = []
    if connection.protocol:
        parts.append(connection.protocol)
    if connection.port:
        parts.append(str(connection.port))
    if connection.purpose:
        parts.append(connection.purpose)

    return " / ".join(parts) if parts else None


def render_connection_arrow(connection: Connection) -> str:
    if connection.direction == "bidirectional":
        return "<-->"
    if connection.direction == "inbound":
        return "<--"
    return "-->"


def append_node_classes(lines: list[str], nodes: list[Node]) -> None:
    if not nodes:
        return

    class_names_by_type: dict[str, list[str]] = {}
    for node in nodes:
        class_names_by_type.setdefault(node.type, []).append(sanitize_id(node.id))

    for node_type in sorted(class_names_by_type):
        class_name = sanitize_class_name(node_type)
        lines.append(f"  classDef {class_name} {NODE_CLASS_STYLES[node_type]}")

    for node_type in sorted(class_names_by_type):
        class_name = sanitize_class_name(node_type)
        node_ids = ",".join(class_names_by_type[node_type])
        lines.append(f"  class {node_ids} {class_name}")


def sanitize_class_name(value: str) -> str:
    return f"type_{sanitize_id(value)}"


def sanitize_zone_id(value: str) -> str:
    return f"zone_{sanitize_id(value)}"


def sanitize_id(value: str) -> str:
    sanitized = re.sub(r"[^0-9A-Za-z_]", "_", value)
    if not sanitized:
        raise ValueError("Node id cannot be empty after sanitization")
    if sanitized[0].isdigit():
        return f"node_{sanitized}"
    return sanitized


def escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def escape_comment(value: str) -> str:
    return value.replace("\n", " ")
