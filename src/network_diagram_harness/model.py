from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
import re
from typing import Any


ALLOWED_DIRECTIONS = {"TB", "TD", "BT", "RL", "LR"}
ALLOWED_NODE_TYPES = {
    "database",
    "external",
    "firewall",
    "load_balancer",
    "network",
    "server",
    "subnet",
}
ALLOWED_CONNECTION_DIRECTIONS = {"outbound", "inbound", "bidirectional"}
PROTOCOL_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+._-]*$")


@dataclass(frozen=True)
class Zone:
    id: str
    name: str
    description: str | None = None


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    type: str
    zone: str | None = None
    ip: str | None = None
    role: str | None = None
    environment: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class Connection:
    source: str
    target: str
    label: str | None = None
    protocol: str | None = None
    port: int | str | None = None
    purpose: str | None = None
    direction: str = "outbound"


@dataclass(frozen=True)
class Diagram:
    title: str | None
    direction: str
    zones: list[Zone]
    nodes: list[Node]
    connections: list[Connection]


def parse_diagram(data: dict[str, Any]) -> Diagram:
    zones = [
        Zone(
            id=str(item["id"]),
            name=str(item.get("name", item["id"])),
            description=str(item["description"]) if item.get("description") else None,
        )
        for item in data.get("zones", [])
    ]

    nodes = [
        Node(
            id=str(item["id"]),
            name=str(item.get("name", item["id"])),
            type=str(item.get("type", "server")),
            zone=str(item["zone"]) if item.get("zone") is not None else None,
            ip=str(item["ip"]) if item.get("ip") is not None else None,
            role=str(item["role"]) if item.get("role") is not None else None,
            environment=str(item["environment"])
            if item.get("environment") is not None
            else None,
            description=str(item["description"])
            if item.get("description") is not None
            else None,
        )
        for item in data.get("nodes", [])
    ]

    connections = [
        Connection(
            source=str(item["source"]),
            target=str(item["target"]),
            label=str(item["label"]) if item.get("label") is not None else None,
            protocol=str(item["protocol"]) if item.get("protocol") is not None else None,
            port=parse_port(item.get("port")),
            purpose=str(item["purpose"]) if item.get("purpose") is not None else None,
            direction=str(item.get("direction", "outbound")),
        )
        for item in data.get("connections", [])
    ]

    diagram = Diagram(
        title=str(data["title"]) if data.get("title") else None,
        direction=str(data.get("direction", "LR")),
        zones=zones,
        nodes=nodes,
        connections=connections,
    )
    validate_diagram(diagram)
    return diagram


def validate_diagram(diagram: Diagram) -> None:
    if diagram.direction not in ALLOWED_DIRECTIONS:
        raise ValueError(f"Unsupported Mermaid direction: {diagram.direction}")

    zone_ids = [zone.id for zone in diagram.zones]
    duplicated_zones = sorted(
        {zone_id for zone_id in zone_ids if zone_ids.count(zone_id) > 1}
    )
    if duplicated_zones:
        raise ValueError(f"Duplicated zone ids: {', '.join(duplicated_zones)}")

    node_ids = [node.id for node in diagram.nodes]
    duplicated = sorted({node_id for node_id in node_ids if node_ids.count(node_id) > 1})
    if duplicated:
        raise ValueError(f"Duplicated node ids: {', '.join(duplicated)}")

    known_zones = set(zone_ids)
    for node in diagram.nodes:
        if node.type not in ALLOWED_NODE_TYPES:
            raise ValueError(f"Unsupported node type: {node.type}")
        if node.zone and node.zone not in known_zones:
            raise ValueError(f"Unknown node zone: {node.zone}")
        if node.ip:
            validate_ip_address(node.ip)

    known_nodes = set(node_ids)
    for connection in diagram.connections:
        if connection.source not in known_nodes:
            raise ValueError(f"Unknown connection source: {connection.source}")
        if connection.target not in known_nodes:
            raise ValueError(f"Unknown connection target: {connection.target}")
        if connection.direction not in ALLOWED_CONNECTION_DIRECTIONS:
            raise ValueError(f"Unsupported connection direction: {connection.direction}")
        if connection.protocol:
            validate_protocol(connection.protocol)


def parse_port(value: Any) -> int | str | None:
    if value is None:
        return None
    if isinstance(value, int):
        validate_port_number(value)
        return value

    port = str(value)
    if "-" in port:
        start, end = port.split("-", maxsplit=1)
        start_number = parse_port_number(start, port)
        end_number = parse_port_number(end, port)
        validate_port_number(start_number)
        validate_port_number(end_number)
        if start_number > end_number:
            raise ValueError(f"Invalid port range: {port}")
        return port

    port_number = parse_port_number(port, port)
    validate_port_number(port_number)
    return port_number


def parse_port_number(value: str, original: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"Invalid port value: {original}") from error


def validate_port_number(value: int) -> None:
    if value < 1 or value > 65535:
        raise ValueError(f"Port must be between 1 and 65535: {value}")


def validate_ip_address(value: str) -> None:
    try:
        ip_address(value)
    except ValueError as error:
        raise ValueError(f"Invalid node ip address: {value}") from error


def validate_protocol(value: str) -> None:
    if not PROTOCOL_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid connection protocol: {value}")
