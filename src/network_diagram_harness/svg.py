from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import textwrap

from .model import Connection, Diagram, Node, Zone


SVG_WIDTH = 1400
SVG_HEIGHT = 920


ZONE_STYLES = {
    "internet": ("#f8fafc", "#94a3b8"),
    "cloud": ("#fefce8", "#ca8a04"),
    "edge": ("#fff7ed", "#f97316"),
    "dmz": ("#fff7ed", "#f97316"),
    "internal": ("#f0fdf4", "#16a34a"),
}

NODE_STYLES = {
    "database": ("#fef3c7", "#b45309"),
    "external": ("#e0f2fe", "#0369a1"),
    "firewall": ("#fee2e2", "#b91c1c"),
    "load_balancer": ("#dcfce7", "#15803d"),
    "network": ("#f1f5f9", "#475569"),
    "server": ("#ede9fe", "#6d28d9"),
    "subnet": ("#ecfeff", "#0e7490"),
}


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


def render_layout_svg(diagram: Diagram) -> str:
    if diagram.layout.profile != "home_lab":
        raise ValueError("SVG layout rendering requires layout.profile: home_lab")

    zone_boxes = build_zone_boxes(diagram.zones)
    node_boxes = build_node_boxes(diagram.nodes, zone_boxes)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" '
            f'height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">'
        ),
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #111827; }",
        ".title { font-size: 24px; font-weight: 700; }",
        ".zone-title { font-size: 14px; font-weight: 700; }",
        ".node-title { font-size: 14px; font-weight: 700; }",
        ".node-detail { font-size: 12px; }",
        ".edge-label { font-size: 11px; fill: #374151; }",
        "</style>",
        '<rect x="0" y="0" width="1400" height="920" fill="#ffffff"/>',
    ]

    if diagram.title:
        lines.append(
            f'<text x="40" y="38" class="title">{escape(diagram.title)}</text>'
        )

    lines.extend(render_marker())

    for zone in diagram.zones:
        box = zone_boxes.get(zone.id)
        if box is not None:
            lines.extend(render_zone(zone, box))

    for connection in diagram.connections:
        source = node_boxes.get(connection.source)
        target = node_boxes.get(connection.target)
        if source is not None and target is not None:
            lines.extend(render_connection(connection, source, target))

    for node in diagram.nodes:
        box = node_boxes.get(node.id)
        if box is not None:
            lines.extend(render_node(node, box))

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def write_layout_svg(diagram: Diagram, output_path: Path) -> None:
    if output_path.suffix.lower() != ".svg":
        raise ValueError("Layout export currently supports .svg output only")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_layout_svg(diagram), encoding="utf-8")


def build_zone_boxes(zones: list[Zone]) -> dict[str, Box]:
    boxes: dict[str, Box] = {}
    for zone in zones:
        category = classify_zone(zone)
        if category == "internet":
            boxes[zone.id] = Box(380, 60, 640, 110)
        elif category == "cloud":
            boxes[zone.id] = Box(40, 230, 240, 540)
        elif category == "edge":
            boxes[zone.id] = Box(1070, 230, 290, 300)
        elif category == "dmz":
            boxes[zone.id] = Box(1070, 580, 290, 260)
        elif category == "internal":
            boxes[zone.id] = Box(320, 300, 700, 540)
        elif zone.id.startswith("vlan"):
            boxes[zone.id] = Box(0, 0, 0, 0)
        else:
            boxes[zone.id] = Box(320, 300, 700, 540)
    return boxes


def build_node_boxes(nodes: list[Node], zone_boxes: dict[str, Box]) -> dict[str, Box]:
    boxes: dict[str, Box] = {}
    zone_counts: dict[str, int] = {}

    for node in nodes:
        category = classify_node(node)
        if category == "internet":
            boxes[node.id] = Box(460, 92, 180, 58)
        elif category == "isp_edge":
            boxes[node.id] = Box(760, 92, 210, 58)
        elif category == "cloud_cdn":
            boxes[node.id] = Box(70, 290, 180, 62)
        elif category == "cloud_storage":
            boxes[node.id] = Box(75, 610, 170, 72)
        elif category == "edge_router":
            boxes[node.id] = Box(1135, 310, 160, 160)
        elif category == "dmz_host":
            boxes[node.id] = Box(1125, 700, 180, 70)
        elif category == "internal_router":
            boxes[node.id] = Box(595, 520, 160, 160)
        elif category == "monitoring":
            boxes[node.id] = Box(585, 365, 180, 72)
        elif category == "client":
            boxes[node.id] = Box(360, 730, 150, 62)
        elif category == "server":
            boxes[node.id] = Box(540, 730, 150, 62)
        elif category == "wifi":
            boxes[node.id] = Box(720, 730, 150, 62)
        elif category == "test":
            boxes[node.id] = Box(900, 730, 150, 62)
        else:
            zone = node.zone or "default"
            count = zone_counts.get(zone, 0)
            zone_counts[zone] = count + 1
            boxes[node.id] = next_box_in_zone(zone_boxes.get(zone), count)

    return boxes


def classify_zone(zone: Zone) -> str:
    value = f"{zone.id} {zone.name}".lower()
    if "internet" in value:
        return "internet"
    if "aws" in value or "cloud" in value:
        return "cloud"
    if "home_edge" in value or "edge" in value:
        return "edge"
    if "dmz" in value or "service zone" in value:
        return "dmz"
    if "internal" in value:
        return "internal"
    return "other"


def classify_node(node: Node) -> str:
    value = f"{node.id} {node.name} {node.role or ''}".lower()
    if "cloudfront" in value or "cdn" in value:
        return "cloud_cdn"
    if "s3" in value or "object storage" in value:
        return "cloud_storage"
    if "isp" in value:
        return "isp_edge"
    if "internet" in value or "isp" in value:
        return "internet"
    if "ax1800" in value or "edge router" in value:
        return "edge_router"
    if "er605" in value or "internal router" in value:
        return "internal_router"
    if "monitoring" in value or "raspberry" in value:
        return "monitoring"
    if "vlan10" in value or "client" in value or "sg108e" in value:
        return "client"
    if "vlan20" in value or "server segment" in value:
        return "server"
    if "vlan30" in value or "wi-fi" in value or "wifi" in value:
        return "wifi"
    if "vlan40" in value or "test" in value:
        return "test"
    if "ubuntu" in value or "lab service host" in value:
        return "dmz_host"
    return "generic"


def next_box_in_zone(zone_box: Box | None, index: int) -> Box:
    if zone_box is None or zone_box.width == 0:
        return Box(60 + index * 180, 120, 150, 62)
    columns = max(1, zone_box.width // 190)
    col = index % columns
    row = index // columns
    return Box(zone_box.x + 40 + col * 180, zone_box.y + 70 + row * 110, 150, 62)


def render_marker() -> list[str]:
    return [
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" '
        'refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#475569"/>',
        "</marker></defs>",
    ]


def render_zone(zone: Zone, box: Box) -> list[str]:
    if box.width == 0 or box.height == 0:
        return []
    category = classify_zone(zone)
    fill, stroke = ZONE_STYLES.get(category, ("#f8fafc", "#cbd5e1"))
    return [
        (
            f'<rect x="{box.x}" y="{box.y}" width="{box.width}" '
            f'height="{box.height}" rx="8" fill="{fill}" stroke="{stroke}"/>'
        ),
        (
            f'<text x="{box.x + 14}" y="{box.y + 24}" '
            f'class="zone-title">{escape(zone.name)}</text>'
        ),
    ]


def render_node(node: Node, box: Box) -> list[str]:
    fill, stroke = NODE_STYLES[node.type]
    label_lines = wrap_label(node.name, 22)
    detail = " / ".join(value for value in [node.ip, node.role] if value)
    detail_lines = wrap_label(detail, 24) if detail else []
    lines = []

    if node.type == "database":
        lines.extend(render_database_node(box, fill, stroke))
    elif node.type == "firewall":
        lines.append(render_diamond_node(box, fill, stroke))
    elif node.type in {"external", "load_balancer"}:
        lines.append(render_rounded_node(box, fill, stroke))
    else:
        lines.append(render_rect_node(box, fill, stroke))

    text_y = box.y + 24
    for line in label_lines:
        lines.append(
            f'<text x="{box.center_x}" y="{text_y}" text-anchor="middle" '
            f'class="node-title">{escape(line)}</text>'
        )
        text_y += 17
    for line in detail_lines:
        lines.append(
            f'<text x="{box.center_x}" y="{text_y}" text-anchor="middle" '
            f'class="node-detail">{escape(line)}</text>'
        )
        text_y += 15
    return lines


def render_rect_node(box: Box, fill: str, stroke: str) -> str:
    return (
        f'<rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" '
        f'rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    )


def render_rounded_node(box: Box, fill: str, stroke: str) -> str:
    return (
        f'<rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" '
        f'rx="28" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    )


def render_diamond_node(box: Box, fill: str, stroke: str) -> str:
    points = [
        (box.center_x, box.y),
        (box.x + box.width, box.center_y),
        (box.center_x, box.y + box.height),
        (box.x, box.center_y),
    ]
    points_value = " ".join(f"{x},{y}" for x, y in points)
    return (
        f'<polygon points="{points_value}" fill="{fill}" stroke="{stroke}" '
        'stroke-width="1.5"/>'
    )


def render_database_node(box: Box, fill: str, stroke: str) -> list[str]:
    return [
        (
            f'<rect x="{box.x}" y="{box.y + 14}" width="{box.width}" '
            f'height="{box.height - 28}" fill="{fill}" stroke="{stroke}" '
            'stroke-width="1.5"/>'
        ),
        (
            f'<ellipse cx="{box.center_x}" cy="{box.y + 14}" '
            f'rx="{box.width // 2}" ry="14" fill="{fill}" stroke="{stroke}" '
            'stroke-width="1.5"/>'
        ),
        (
            f'<ellipse cx="{box.center_x}" cy="{box.y + box.height - 14}" '
            f'rx="{box.width // 2}" ry="14" fill="{fill}" stroke="{stroke}" '
            'stroke-width="1.5"/>'
        ),
    ]


def render_connection(connection: Connection, source: Box, target: Box) -> list[str]:
    start_x, start_y, end_x, end_y = connection_points(source, target)
    label = connection_label(connection)
    mid_x = (start_x + end_x) // 2
    mid_y = (start_y + end_y) // 2
    lines = [
        (
            f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" '
            'stroke="#475569" stroke-width="1.4" marker-end="url(#arrow)"/>'
        )
    ]
    if label:
        lines.append(
            f'<text x="{mid_x}" y="{mid_y - 6}" text-anchor="middle" '
            f'class="edge-label">{escape(label)}</text>'
        )
    return lines


def connection_points(source: Box, target: Box) -> tuple[int, int, int, int]:
    dx = target.center_x - source.center_x
    dy = target.center_y - source.center_y
    if abs(dx) > abs(dy):
        start_x = source.x + source.width if dx > 0 else source.x
        start_y = source.center_y
        end_x = target.x if dx > 0 else target.x + target.width
        end_y = target.center_y
    else:
        start_x = source.center_x
        start_y = source.y + source.height if dy > 0 else source.y
        end_x = target.center_x
        end_y = target.y if dy > 0 else target.y + target.height
    return start_x, start_y, end_x, end_y


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


def wrap_label(value: str, width: int) -> list[str]:
    if not value:
        return []
    wrapped = textwrap.wrap(value, width=width, break_long_words=False)
    return wrapped or [value]
