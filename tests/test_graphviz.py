from network_diagram_harness.model import parse_diagram
from network_diagram_harness.renderers import get_renderer, renderer_names
from network_diagram_harness.renderers.graphviz import render_graphviz_dot


def test_render_graphviz_dot_with_zones_types_and_edges() -> None:
    diagram = parse_diagram(
        {
            "title": "Graphviz Network",
            "direction": "LR",
            "zones": [
                {"id": "dmz", "name": "DMZ"},
                {"id": "internal", "name": "Internal"},
            ],
            "nodes": [
                {
                    "id": "fw",
                    "name": "Firewall",
                    "type": "firewall",
                    "zone": "dmz",
                },
                {
                    "id": "app",
                    "name": "App Server",
                    "type": "server",
                    "zone": "internal",
                    "ip": "10.0.10.10",
                    "role": "app",
                },
            ],
            "connections": [
                {
                    "source": "fw",
                    "target": "app",
                    "protocol": "HTTPS",
                    "port": 443,
                    "purpose": "application traffic",
                },
            ],
        }
    )

    output = render_graphviz_dot(diagram)

    assert output.startswith("digraph network_diagram {\n")
    assert 'rankdir="LR"' in output
    assert "subgraph cluster_dmz {" in output
    assert "subgraph cluster_internal {" in output
    assert 'fw [label="Firewall", shape="diamond"' in output
    assert 'app [label="App Server\\n10.0.10.10 / app", shape="box"' in output
    assert 'fw -> app [label="HTTPS / 443 / application traffic"];' in output


def test_render_graphviz_dot_handles_bidirectional_and_inbound_edges() -> None:
    diagram = parse_diagram(
        {
            "nodes": [
                {"id": "client", "name": "Client", "type": "external"},
                {"id": "server", "name": "Server", "type": "server"},
                {"id": "database", "name": "Database", "type": "database"},
            ],
            "connections": [
                {
                    "source": "client",
                    "target": "server",
                    "label": "sync",
                    "direction": "bidirectional",
                },
                {
                    "source": "server",
                    "target": "database",
                    "label": "pull",
                    "direction": "inbound",
                },
            ],
        }
    )

    output = render_graphviz_dot(diagram)

    assert 'client -> server [label="sync", dir="both"];' in output
    assert 'database -> server [label="pull"];' in output


def test_graphviz_renderer_is_registered() -> None:
    renderer = get_renderer("graphviz")

    assert renderer.name == "graphviz"
    assert renderer.source_suffix == ".dot"


def test_renderer_names_are_sorted() -> None:
    assert renderer_names() == ("graphviz", "mermaid")
