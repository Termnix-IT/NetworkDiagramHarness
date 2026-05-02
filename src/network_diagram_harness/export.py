from __future__ import annotations

import subprocess
from pathlib import Path

from .io import load_diagram
from .mermaid import render_mermaid
from .model import Diagram


SUPPORTED_EXPORT_FORMATS = {".svg", ".png", ".pdf"}


def export_with_mermaid_cli(
    diagram: Diagram,
    output_path: Path,
    mmdc_command: str = "mmdc",
) -> None:
    suffix = output_path.suffix.lower()
    if suffix not in SUPPORTED_EXPORT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_EXPORT_FORMATS))
        raise ValueError(f"Unsupported export format: {suffix}. Use one of: {supported}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_input = output_path.with_suffix(f"{output_path.suffix}.mmd")
    temp_input.write_text(render_mermaid(diagram), encoding="utf-8")

    try:
        subprocess.run(
            [
                mmdc_command,
                "--input",
                str(temp_input),
                "--output",
                str(output_path),
            ],
            check=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Mermaid CLI executable was not found. Install @mermaid-js/mermaid-cli "
            "and make the mmdc command available on PATH."
        ) from error
    finally:
        temp_input.unlink(missing_ok=True)


def export_directory_with_mermaid_cli(
    input_dir: Path,
    output_dir: Path,
    image_format: str = "svg",
    mmdc_command: str = "mmdc",
) -> list[Path]:
    suffix = normalize_export_suffix(image_format)
    if suffix not in SUPPORTED_EXPORT_FORMATS:
        supported = ", ".join(sorted(format.lstrip(".") for format in SUPPORTED_EXPORT_FORMATS))
        raise ValueError(f"Unsupported export format: {image_format}. Use one of: {supported}")

    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")

    output_paths = []
    for input_path in sorted(input_dir.glob("*.yml")):
        diagram = load_diagram(input_path)
        output_path = output_dir / f"{input_path.stem}{suffix}"
        export_with_mermaid_cli(diagram, output_path, mmdc_command)
        output_paths.append(output_path)

    return output_paths


def normalize_export_suffix(value: str) -> str:
    return value if value.startswith(".") else f".{value}"
