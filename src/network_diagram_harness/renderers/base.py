from __future__ import annotations

from typing import Protocol

from network_diagram_harness.model import Diagram


class DiagramRenderer(Protocol):
    name: str
    source_suffix: str

    def render_source(self, diagram: Diagram) -> str:
        ...
