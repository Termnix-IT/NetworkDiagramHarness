from __future__ import annotations

from network_diagram_harness.mermaid import render_mermaid
from network_diagram_harness.model import Diagram


class MermaidRenderer:
    name = "mermaid"
    source_suffix = ".mmd"

    def render_source(self, diagram: Diagram) -> str:
        return render_mermaid(diagram)
