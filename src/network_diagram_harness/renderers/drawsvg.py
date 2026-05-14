from __future__ import annotations

from dataclasses import dataclass
from html import escape
from math import ceil

from network_diagram_harness.model import Connection, Diagram, Node, Zone
from network_diagram_harness.renderers.styles import node_style_profile, zone_style_profile


SVG_MIN_WIDTH = 1400
SVG_MARGIN = 28
ZONE_WIDTH = 300
ZONE_GAP = 34
ZONE_TOP = 88
NODE_WIDTH = 210
NODE_HEIGHT = 68
NODE_GAP = 26


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2


class DrawsvgRenderer:
    name = "drawsvg"
    source_suffix = ".svg"

    def render_source(self, diagram: Diagram) -> str:
        return render_drawsvg_svg(diagram)


def render_drawsvg_svg(diagram: Diagram) -> str:
    zone_boxes, node_boxes = build_layout(diagram)
    width = max(
        [box.x + box.width + SVG_MARGIN for box in zone_boxes.values()]
        + [box.x + box.width + SVG_MARGIN for box in node_boxes.values()]
        + [SVG_MIN_WIDTH]
    )
    height = max(
        [box.y + box.height + 48 for box in zone_boxes.values()]
        + [box.y + box.height + 48 for box in node_boxes.values()]
        + [220]
    )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #111827; }",
        ".title { font-size: 22px; font-weight: 700; }",
        ".zone-title { font-size: 14px; font-weight: 700; }",
        ".node-title { font-size: 13px; font-weight: 700; }",
        ".node-detail { font-size: 11px; fill: #374151; }",
        ".edge-label { font-size: 10px; fill: #374151; }",
        "</style>",
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" '
        'refY="3" orient="auto" markerUnits="strokeWidth">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#475569"/></marker></defs>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
    ]

    if diagram.title:
        lines.append(
            f'<text x="{width // 2}" y="42" text-anchor="middle" '
            f'class="title">{escape(diagram.title)}</text>'
        )

    for zone in diagram.zones:
        box = zone_boxes.get(zone.id)
        if box:
            lines.extend(render_zone(diagram, zone, box))

    for connection in diagram.connections:
        source = node_boxes.get(connection.source)
        target = node_boxes.get(connection.target)
        if source and target:
            lines.extend(render_connection(connection, source, target))

    for node in sorted(diagram.nodes, key=lambda item: (item.order is None, item.order or 0, item.id)):
        box = node_boxes[node.id]
        lines.extend(render_node(diagram, node, box))

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def build_layout(diagram: Diagram) -> tuple[dict[str, Box], dict[str, Box]]:
    zone_nodes = {
        zone.id: sorted(
            [node for node in diagram.nodes if node.zone == zone.id],
            key=lambda item: (item.order is None, item.order or 0, item.id),
        )
        for zone in diagram.zones
    }
    unzoned_nodes = sorted(
        [node for node in diagram.nodes if node.zone is None],
        key=lambda item: (item.order is None, item.order or 0, item.id),
    )

    all_zone_ids = [zone.id for zone in diagram.zones if zone_nodes[zone.id]]
    if unzoned_nodes:
        all_zone_ids.append("__default__")

    zone_count = max(1, len(all_zone_ids))
    total_width = zone_count * ZONE_WIDTH + (zone_count - 1) * ZONE_GAP
    start_x = max(SVG_MARGIN, (SVG_MIN_WIDTH - total_width) // 2)

    zone_boxes: dict[str, Box] = {}
    node_boxes: dict[str, Box] = {}
    for index, zone_id in enumerate(all_zone_ids):
        nodes = unzoned_nodes if zone_id == "__default__" else zone_nodes[zone_id]
        rows = max(1, ceil(len(nodes) / 1))
        zone_height = 72 + rows * NODE_HEIGHT + max(0, rows - 1) * NODE_GAP
        x = start_x + index * (ZONE_WIDTH + ZONE_GAP)
        zone_boxes[zone_id] = Box(x, ZONE_TOP, ZONE_WIDTH, zone_height)
        for node_index, node in enumerate(nodes):
            node_boxes[node.id] = Box(
                x + (ZONE_WIDTH - NODE_WIDTH) // 2,
                ZONE_TOP + 48 + node_index * (NODE_HEIGHT + NODE_GAP),
                NODE_WIDTH,
                NODE_HEIGHT,
            )

    return zone_boxes, node_boxes


def render_zone(diagram: Diagram, zone: Zone, box: Box) -> list[str]:
    fill, color = zone_style(diagram, zone.id, zone.name)
    return [
        (
            f'<rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" '
            f'rx="8" fill="{fill}" stroke="{color}" stroke-width="1.4"/>'
        ),
        f'<text x="{box.center_x}" y="{box.y + 26}" text-anchor="middle" class="zone-title">{escape(zone.name)}</text>',
    ]


def render_node(diagram: Diagram, node: Node, box: Box) -> list[str]:
    style = node_style_profile(diagram.style.profile)[node.type]
    lines = [render_node_shape(node, box, style["fillcolor"], style["color"])]
    title_y = box.center_y - 4 if not node_detail(node) else box.center_y - 10
    lines.append(
        f'<text x="{box.center_x}" y="{title_y}" text-anchor="middle" '
        f'class="node-title">{escape(node.name)}</text>'
    )
    detail = node_detail(node)
    if detail:
        lines.append(
            f'<text x="{box.center_x}" y="{title_y + 18}" text-anchor="middle" '
            f'class="node-detail">{escape(detail)}</text>'
        )
    return lines


def render_node_shape(node: Node, box: Box, fill: str, color: str) -> str:
    if node.type == "firewall":
        points = [
            (box.center_x, box.y),
            (box.x + box.width, box.center_y),
            (box.center_x, box.y + box.height),
            (box.x, box.center_y),
        ]
        value = " ".join(f"{x},{y}" for x, y in points)
        return f'<polygon points="{value}" fill="{fill}" stroke="{color}" stroke-width="1.5"/>'
    if node.type == "database":
        return (
            f'<rect x="{box.x}" y="{box.y + 12}" width="{box.width}" height="{box.height - 24}" '
            f'fill="{fill}" stroke="{color}" stroke-width="1.5"/>'
            f'<ellipse cx="{box.center_x}" cy="{box.y + 12}" rx="{box.width // 2}" ry="12" '
            f'fill="{fill}" stroke="{color}" stroke-width="1.5"/>'
            f'<ellipse cx="{box.center_x}" cy="{box.y + box.height - 12}" rx="{box.width // 2}" ry="12" '
            f'fill="{fill}" stroke="{color}" stroke-width="1.5"/>'
        )
    rx = 28 if node.type in {"external", "load_balancer"} else 5
    return (
        f'<rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" '
        f'rx="{rx}" fill="{fill}" stroke="{color}" stroke-width="1.5"/>'
    )


def render_connection(connection: Connection, source: Box, target: Box) -> list[str]:
    start_x, start_y, end_x, end_y = connection_points(source, target)
    label = connection_label(connection)
    marker_start = ' marker-start="url(#arrow)"' if connection.direction == "bidirectional" else ""
    marker_end = ' marker-end="url(#arrow)"'
    lines = [
        (
            f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" '
            f'stroke="#475569" stroke-width="1.3"{marker_start}{marker_end}/>'
        )
    ]
    if label:
        mid_x = (start_x + end_x) // 2
        mid_y = (start_y + end_y) // 2 - 6
        lines.append(
            f'<text x="{mid_x}" y="{mid_y}" text-anchor="middle" '
            f'class="edge-label">{escape(label)}</text>'
        )
    return lines


def connection_points(source: Box, target: Box) -> tuple[int, int, int, int]:
    if source.center_x <= target.center_x:
        return source.x + source.width, source.center_y, target.x, target.center_y
    return source.x, source.center_y, target.x + target.width, target.center_y


def node_detail(node: Node) -> str:
    return " / ".join(value for value in [node.ip, node.role] if value)


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
