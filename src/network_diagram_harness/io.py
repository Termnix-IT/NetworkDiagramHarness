from __future__ import annotations

from pathlib import Path

import yaml

from .model import Diagram, parse_diagram


def load_diagram(path: Path) -> Diagram:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    return parse_diagram(data)


def write_output(output: str, path: Path | None) -> None:
    if path is None:
        print(output, end="")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
