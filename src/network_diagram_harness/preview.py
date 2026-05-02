from __future__ import annotations

from pathlib import Path

from .mermaid import render_mermaid
from .model import Diagram


def render_markdown_preview(diagram: Diagram, source_path: Path) -> str:
    title = diagram.title or source_path.stem
    mermaid = render_mermaid(diagram).rstrip()

    return "\n".join(
        [
            f"# {title}",
            "",
            "## Source",
            "",
            f"`{source_path.as_posix()}`",
            "",
            "## Summary",
            "",
            f"- Zones: `{len(diagram.zones)}`",
            f"- Nodes: `{len(diagram.nodes)}`",
            f"- Connections: `{len(diagram.connections)}`",
            "",
            "## Mermaid Preview",
            "",
            "```mermaid",
            mermaid,
            "```",
            "",
        ]
    )
