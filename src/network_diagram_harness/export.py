from __future__ import annotations

import subprocess
from pathlib import Path

from .io import load_diagram
from .mermaid import render_mermaid
from .model import Diagram
from .renderers.graphviz import render_graphviz_dot


SUPPORTED_EXPORT_FORMATS = {".svg", ".png", ".pdf"}
SUPPORTED_GRAPHVIZ_EXPORT_FORMATS = {".svg", ".png", ".pdf"}


def export_diagram(
    diagram: Diagram,
    output_path: Path,
    renderer: str = "mermaid",
    mmdc_command: str = "mmdc",
    dot_command: str = "dot",
    puppeteer_config_file: Path | None = None,
    width: int | None = None,
    height: int | None = None,
) -> None:
    if renderer == "graphviz":
        export_with_graphviz(diagram, output_path, dot_command)
        return
    if renderer == "mermaid":
        export_with_mermaid_cli(
            diagram,
            output_path,
            mmdc_command,
            puppeteer_config_file,
            width,
            height,
        )
        return

    raise_unsupported_renderer(renderer)


def export_directory(
    input_dir: Path,
    output_dir: Path,
    renderer: str = "mermaid",
    image_format: str = "svg",
    mmdc_command: str = "mmdc",
    dot_command: str = "dot",
    puppeteer_config_file: Path | None = None,
    width: int | None = None,
    height: int | None = None,
) -> list[Path]:
    if renderer == "graphviz":
        return export_directory_with_graphviz(
            input_dir,
            output_dir,
            image_format,
            dot_command,
        )
    if renderer == "mermaid":
        return export_directory_with_mermaid_cli(
            input_dir,
            output_dir,
            image_format,
            mmdc_command,
            puppeteer_config_file,
            width,
            height,
        )

    raise_unsupported_renderer(renderer)


def raise_unsupported_renderer(renderer: str) -> None:
    raise ValueError(f"Unsupported export renderer: {renderer}. Use one of: graphviz, mermaid")


def export_with_mermaid_cli(
    diagram: Diagram,
    output_path: Path,
    mmdc_command: str = "mmdc",
    puppeteer_config_file: Path | None = None,
    width: int | None = None,
    height: int | None = None,
) -> None:
    suffix = output_path.suffix.lower()
    if suffix not in SUPPORTED_EXPORT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_EXPORT_FORMATS))
        raise ValueError(f"Unsupported export format: {suffix}. Use one of: {supported}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_input = output_path.with_suffix(f"{output_path.suffix}.mmd")
    temp_input.write_text(render_mermaid(diagram), encoding="utf-8")

    command = [
        mmdc_command,
        "--input",
        str(temp_input),
        "--output",
        str(output_path),
    ]
    if puppeteer_config_file is not None:
        command.extend(["--puppeteerConfigFile", str(puppeteer_config_file)])
    if width is not None:
        command.extend(["--width", str(width)])
    if height is not None:
        command.extend(["--height", str(height)])

    try:
        subprocess.run(command, check=True)
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
    puppeteer_config_file: Path | None = None,
    width: int | None = None,
    height: int | None = None,
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
        export_with_mermaid_cli(
            diagram,
            output_path,
            mmdc_command,
            puppeteer_config_file,
            width,
            height,
        )
        output_paths.append(output_path)

    return output_paths


def export_with_graphviz(
    diagram: Diagram,
    output_path: Path,
    dot_command: str = "dot",
) -> None:
    suffix = output_path.suffix.lower()
    if suffix not in SUPPORTED_GRAPHVIZ_EXPORT_FORMATS:
        supported = ", ".join(sorted(SUPPORTED_GRAPHVIZ_EXPORT_FORMATS))
        raise ValueError(f"Unsupported Graphviz export format: {suffix}. Use one of: {supported}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_input = output_path.with_suffix(f"{output_path.suffix}.dot")
    temp_input.write_text(render_graphviz_dot(diagram), encoding="utf-8")

    command = [
        dot_command,
        f"-T{suffix.lstrip('.')}",
        str(temp_input),
        "-o",
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            "Graphviz dot executable was not found. Install Graphviz "
            "and make the dot command available on PATH."
        ) from error
    finally:
        temp_input.unlink(missing_ok=True)


def export_directory_with_graphviz(
    input_dir: Path,
    output_dir: Path,
    image_format: str = "svg",
    dot_command: str = "dot",
) -> list[Path]:
    suffix = normalize_export_suffix(image_format)
    if suffix not in SUPPORTED_GRAPHVIZ_EXPORT_FORMATS:
        supported = ", ".join(
            sorted(format.lstrip(".") for format in SUPPORTED_GRAPHVIZ_EXPORT_FORMATS)
        )
        raise ValueError(f"Unsupported Graphviz export format: {image_format}. Use one of: {supported}")

    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")

    output_paths = []
    for input_path in sorted(input_dir.glob("*.yml")):
        diagram = load_diagram(input_path)
        output_path = output_dir / f"{input_path.stem}{suffix}"
        export_with_graphviz(diagram, output_path, dot_command)
        output_paths.append(output_path)

    return output_paths


def normalize_export_suffix(value: str) -> str:
    return value if value.startswith(".") else f".{value}"
