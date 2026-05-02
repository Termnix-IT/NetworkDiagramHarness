from pathlib import Path

from network_diagram_harness.model import parse_diagram
from network_diagram_harness.preview import render_markdown_preview


def test_render_markdown_preview() -> None:
    diagram = parse_diagram(
        {
            "title": "Preview Network",
            "nodes": [
                {"id": "web", "name": "Web Server", "type": "server"},
            ],
        }
    )

    output = render_markdown_preview(diagram, Path("examples/preview.yml"))

    assert "# Preview Network" in output
    assert "`examples/preview.yml`" in output
    assert "- Nodes: `1`" in output
    assert "```mermaid\nflowchart LR" in output
