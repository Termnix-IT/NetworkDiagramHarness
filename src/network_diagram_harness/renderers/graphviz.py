from __future__ import annotations

import re

from network_diagram_harness.model import Connection, Diagram, Node
from network_diagram_harness.renderers.styles import (
    node_style_profile,
    zone_style_profile,
)


RANK_DIRECTIONS = {
    "BT": "BT",
    "LR": "LR",
    "RL": "RL",
    "TB": "TB",
    "TD": "TB",
}

NODE_STYLES = {
    "database": {
        "shape": "cylinder",
    },
    "external": {
        "shape": "oval",
    },
    "firewall": {
        "shape": "diamond",
    },
    "load_balancer": {
        "shape": "component",
    },
    "network": {
        "shape": "box3d",
    },
    "server": {
        "shape": "box",
    },
    "subnet": {
        "shape": "folder",
    },
}


class GraphvizRenderer:
    name = "graphviz"
    source_suffix = ".dot"

    def render_source(self, diagram: Diagram) -> str:
        return render_graphviz_dot(diagram)


def render_graphviz_dot(diagram: Diagram) -> str:
    lines = [
        "digraph network_diagram {",
        f"  graph [{format_attributes(graph_attributes(diagram))}];",
        "  node [fontname=\"Arial\", fontsize=\"11\", style=\"rounded,filled\", margin=\"0.10,0.06\"];",
        "  edge [fontname=\"Arial\", fontsize=\"10\", color=\"#475569\", arrowsize=\"0.8\"];",
    ]

    if diagram.title:
        lines.append(f"  labelloc=\"t\";")
        lines.append(f"  label={quote(diagram.title)};")

    rendered_nodes = set()
    nodes_by_zone = {
        zone.id: [node for node in diagram.nodes if node.zone == zone.id]
        for zone in diagram.zones
    }

    for zone in diagram.zones:
        zone_nodes = nodes_by_zone[zone.id]
        if not zone_nodes:
            continue

        fill, color = zone_style(diagram, zone.id, zone.name)
        lines.append(f"  subgraph {cluster_id(zone.id)} {{")
        lines.append(f"    graph [{format_attributes(cluster_attributes(zone.name, fill, color))}];")
        for node in sort_nodes(zone_nodes):
            lines.append(f"    {node_id(node.id)} [{format_attributes(node_attributes(diagram, node))}];")
            rendered_nodes.add(node.id)
        lines.append("  }")

    for node in sort_nodes(diagram.nodes):
        if node.id not in rendered_nodes:
            lines.append(f"  {node_id(node.id)} [{format_attributes(node_attributes(diagram, node))}];")

    lines.extend(render_rank_hints(diagram))

    for connection in diagram.connections:
        lines.append(render_edge(connection))

    lines.append("}")
    return "\n".join(lines) + "\n"


def graph_attributes(diagram: Diagram) -> dict[str, str]:
    return {
        "rankdir": RANK_DIRECTIONS[diagram.direction],
        "bgcolor": "white",
        "compound": "true",
        "concentrate": "false",
        "nodesep": "0.70",
        "ranksep": "0.95",
        "splines": "polyline",
        "pad": "0.35",
    }


def cluster_attributes(name: str, fill: str, color: str) -> dict[str, str]:
    return {
        "label": name,
        "style": "rounded,filled",
        "fillcolor": fill,
        "color": color,
        "fontname": "Arial",
        "fontsize": "13",
        "penwidth": "1.4",
        "margin": "24",
    }


def node_attributes(diagram: Diagram, node: Node) -> dict[str, str]:
    shape_style = NODE_STYLES[node.type]
    color_style = node_style_profile(diagram.style.profile)[node.type]
    attributes = {
        "label": render_node_label(node),
        "shape": shape_style["shape"],
        "fillcolor": color_style["fillcolor"],
        "color": color_style["color"],
        "penwidth": "1.5",
    }
    if node.group:
        attributes["group"] = node.group
    if node.type == "firewall":
        attributes["margin"] = "0.16,0.10"
    if node.type in {"external", "load_balancer"}:
        attributes["style"] = "filled"
    return attributes


def render_node_label(node: Node) -> str:
    details = [value for value in [node.ip, node.role] if value]
    if not details:
        return node.name
    return f"{node.name}\n{' / '.join(details)}"


def render_edge(connection: Connection) -> str:
    source = node_id(connection.source)
    target = node_id(connection.target)
    attributes: dict[str, str] = {}
    label = render_connection_label(connection)
    if label:
        attributes["label"] = label

    if connection.direction == "inbound":
        source, target = target, source
    elif connection.direction == "bidirectional":
        attributes["dir"] = "both"

    return f"  {source} -> {target} [{format_attributes(attributes)}];"


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


def render_rank_hints(diagram: Diagram) -> list[str]:
    rank_nodes: dict[str, list[Node]] = {}
    for node in diagram.nodes:
        if node.rank:
            rank_nodes.setdefault(node.rank, []).append(node)

    lines = []
    for rank in sorted(rank_nodes):
        ids = "; ".join(node_id(node.id) for node in sort_nodes(rank_nodes[rank]))
        lines.append(f"  {{ rank={quote(rank)}; {ids}; }}")
    return lines


def sort_nodes(nodes: list[Node]) -> list[Node]:
    return sorted(nodes, key=lambda node: (node.order is None, node.order or 0, node.id))


def zone_style(diagram: Diagram, zone_id: str, zone_name: str) -> tuple[str, str]:
    value = f"{zone_id} {zone_name}".lower()
    styles = zone_style_profile(diagram.style.profile)
    if "internet" in value:
        return styles["internet"]
    if "aws" in value or "cloud" in value:
        return styles["cloud"]
    if "edge" in value:
        return styles["edge"]
    if "dmz" in value:
        return styles["dmz"]
    if "internal" in value:
        return styles["internal"]
    return styles["other"]


def format_attributes(attributes: dict[str, str]) -> str:
    return ", ".join(f"{key}={quote(value)}" for key, value in attributes.items())


def quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f"\"{escaped}\""


def cluster_id(value: str) -> str:
    return f"cluster_{sanitize_id(value)}"


def node_id(value: str) -> str:
    return sanitize_id(value)


def sanitize_id(value: str) -> str:
    sanitized = re.sub(r"[^0-9A-Za-z_]", "_", value)
    if not sanitized:
        raise ValueError("Graphviz id cannot be empty after sanitization")
    if sanitized[0].isdigit():
        return f"node_{sanitized}"
    return sanitized
