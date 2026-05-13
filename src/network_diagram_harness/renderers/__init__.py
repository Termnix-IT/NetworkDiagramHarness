from __future__ import annotations

from .base import DiagramRenderer
from .graphviz import GraphvizRenderer
from .mermaid import MermaidRenderer


RENDERERS: dict[str, DiagramRenderer] = {
    "graphviz": GraphvizRenderer(),
    "mermaid": MermaidRenderer(),
}


def renderer_names() -> tuple[str, ...]:
    return tuple(sorted(RENDERERS))


def get_renderer(name: str) -> DiagramRenderer:
    try:
        return RENDERERS[name]
    except KeyError as error:
        supported = ", ".join(sorted(RENDERERS))
        raise ValueError(f"Unsupported renderer: {name}. Use one of: {supported}") from error
