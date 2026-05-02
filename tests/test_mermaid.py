from network_diagram_harness.mermaid import render_mermaid
from network_diagram_harness.model import parse_diagram


def test_render_simple_diagram() -> None:
    diagram = parse_diagram(
        {
            "title": "Simple Network",
            "nodes": [
                {"id": "internet", "name": "Internet", "type": "external"},
                {"id": "web", "name": "Web Server", "type": "server"},
            ],
            "connections": [
                {"source": "internet", "target": "web", "label": "HTTPS 443"},
            ],
        }
    )

    assert render_mermaid(diagram) == (
        "flowchart LR\n"
        "  %% Simple Network\n"
        '  internet(["Internet"])\n'
        '  web["Web Server"]\n'
        '  internet -->|"HTTPS 443"| web\n'
        "  classDef type_external fill:#e0f2fe,stroke:#0369a1,color:#111827\n"
        "  classDef type_server fill:#ede9fe,stroke:#6d28d9,color:#111827\n"
        "  class internet type_external\n"
        "  class web type_server\n"
    )


def test_unknown_connection_source_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [{"id": "web", "name": "Web Server"}],
                "connections": [{"source": "internet", "target": "web"}],
            }
        )
    except ValueError as error:
        assert "Unknown connection source: internet" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_render_zoned_diagram_with_connection_metadata() -> None:
    diagram = parse_diagram(
        {
            "zones": [
                {"id": "dmz", "name": "DMZ"},
                {"id": "app", "name": "Application Segment"},
            ],
            "nodes": [
                {
                    "id": "lb",
                    "name": "Load Balancer",
                    "type": "load_balancer",
                    "zone": "dmz",
                    "ip": "10.0.1.10",
                    "role": "ingress",
                },
                {
                    "id": "web",
                    "name": "Web Server",
                    "type": "server",
                    "zone": "app",
                    "ip": "10.0.10.11",
                    "role": "web",
                },
            ],
            "connections": [
                {
                    "source": "lb",
                    "target": "web",
                    "protocol": "HTTP",
                    "port": 8080,
                    "purpose": "application traffic",
                },
            ],
        }
    )

    assert render_mermaid(diagram) == (
        "flowchart LR\n"
        '  subgraph zone_dmz["DMZ"]\n'
        '    lb(["Load Balancer<br/>10.0.1.10 / ingress"])\n'
        "  end\n"
        '  subgraph zone_app["Application Segment"]\n'
        '    web["Web Server<br/>10.0.10.11 / web"]\n'
        "  end\n"
        '  lb -->|"HTTP / 8080 / application traffic"| web\n'
        "  classDef type_load_balancer fill:#dcfce7,stroke:#15803d,color:#111827\n"
        "  classDef type_server fill:#ede9fe,stroke:#6d28d9,color:#111827\n"
        "  class lb type_load_balancer\n"
        "  class web type_server\n"
    )


def test_unknown_node_zone_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "zones": [{"id": "dmz", "name": "DMZ"}],
                "nodes": [{"id": "web", "name": "Web Server", "zone": "app"}],
            }
        )
    except ValueError as error:
        assert "Unknown node zone: app" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_port_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [
                    {"id": "source", "name": "Source"},
                    {"id": "target", "name": "Target"},
                ],
                "connections": [
                    {"source": "source", "target": "target", "port": 70000},
                ],
            }
        )
    except ValueError as error:
        assert "Port must be between 1 and 65535: 70000" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_unknown_node_type_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [
                    {"id": "web", "name": "Web Server", "type": "unknown_type"},
                ],
            }
        )
    except ValueError as error:
        assert "Unsupported node type: unknown_type" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_ip_address_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [
                    {"id": "web", "name": "Web Server", "ip": "999.0.0.1"},
                ],
            }
        )
    except ValueError as error:
        assert "Invalid node ip address: 999.0.0.1" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_protocol_is_rejected() -> None:
    try:
        parse_diagram(
            {
                "nodes": [
                    {"id": "source", "name": "Source"},
                    {"id": "target", "name": "Target"},
                ],
                "connections": [
                    {
                        "source": "source",
                        "target": "target",
                        "protocol": "HTTP API",
                    },
                ],
            }
        )
    except ValueError as error:
        assert "Invalid connection protocol: HTTP API" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_port_string_is_rejected_with_clear_error() -> None:
    try:
        parse_diagram(
            {
                "nodes": [
                    {"id": "source", "name": "Source"},
                    {"id": "target", "name": "Target"},
                ],
                "connections": [
                    {"source": "source", "target": "target", "port": "https"},
                ],
            }
        )
    except ValueError as error:
        assert "Invalid port value: https" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_unused_node_type_class_definitions_are_not_rendered() -> None:
    diagram = parse_diagram(
        {
            "nodes": [
                {"id": "web", "name": "Web Server", "type": "server"},
            ],
        }
    )

    output = render_mermaid(diagram)

    assert "classDef type_server" in output
    assert "classDef type_database" not in output


def test_zone_id_can_match_node_id_without_mermaid_cycle() -> None:
    diagram = parse_diagram(
        {
            "zones": [{"id": "internet", "name": "Internet"}],
            "nodes": [
                {
                    "id": "internet",
                    "name": "Internet",
                    "type": "external",
                    "zone": "internet",
                },
            ],
        }
    )

    output = render_mermaid(diagram)

    assert 'subgraph zone_internet["Internet"]' in output
    assert 'internet(["Internet"])' in output
    assert 'subgraph internet["Internet"]' not in output
