from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .io import load_diagram, write_output
from .export import export_directory_with_mermaid_cli, export_with_mermaid_cli
from .mermaid import render_mermaid
from .preview import render_markdown_preview
from .svg import export_layout


COMMANDS = {"export", "export-all", "export-layout", "render", "validate", "preview"}


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_command_parser() if argv[:1] and argv[0] in COMMANDS else build_legacy_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "render":
            run_render(args)
            return

        if args.command == "validate":
            run_validate(args)
            return

        if args.command == "preview":
            run_preview(args)
            return

        if args.command == "export":
            run_export(args)
            return

        if args.command == "export-all":
            run_export_all(args)
            return

        if args.command == "export-layout":
            run_export_layout(args)
            return
    except (RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    parser.error(f"Unknown command: {args.command}")


def build_legacy_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Mermaid network diagrams from YAML definitions.",
    )
    parser.set_defaults(command="render")
    parser.add_argument("input", type=Path, help="Path to a YAML diagram definition.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to write the generated Mermaid file. Prints to stdout when omitted.",
    )
    return parser


def build_command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate network diagrams from YAML definitions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser(
        "render",
        help="Render a YAML diagram definition to Mermaid.",
    )
    render_parser.add_argument("input", type=Path)
    render_parser.add_argument("-o", "--output", type=Path)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a YAML diagram definition.",
    )
    validate_parser.add_argument("input", type=Path)

    preview_parser = subparsers.add_parser(
        "preview",
        help="Render a Markdown preview with an embedded Mermaid block.",
    )
    preview_parser.add_argument("input", type=Path)
    preview_parser.add_argument("-o", "--output", type=Path)

    export_parser = subparsers.add_parser(
        "export",
        help="Export a diagram to SVG, PNG, or PDF using Mermaid CLI.",
    )
    export_parser.add_argument("input", type=Path)
    export_parser.add_argument("-o", "--output", type=Path, required=True)
    export_parser.add_argument(
        "--mmdc",
        default="mmdc",
        help="Mermaid CLI executable. Defaults to mmdc.",
    )
    export_parser.add_argument(
        "--puppeteer-config-file",
        type=Path,
        help="Puppeteer JSON config file passed to Mermaid CLI.",
    )
    export_parser.add_argument("--width", type=int, help="Output viewport width.")
    export_parser.add_argument("--height", type=int, help="Output viewport height.")

    export_all_parser = subparsers.add_parser(
        "export-all",
        help="Export every *.yml diagram in a directory to SVG, PNG, or PDF.",
    )
    export_all_parser.add_argument("input_dir", type=Path)
    export_all_parser.add_argument("-o", "--output-dir", type=Path, required=True)
    export_all_parser.add_argument(
        "--format",
        default="svg",
        choices=["svg", "png", "pdf"],
        help="Image format to generate. Defaults to svg.",
    )
    export_all_parser.add_argument(
        "--mmdc",
        default="mmdc",
        help="Mermaid CLI executable. Defaults to mmdc.",
    )
    export_all_parser.add_argument(
        "--puppeteer-config-file",
        type=Path,
        help="Puppeteer JSON config file passed to Mermaid CLI.",
    )
    export_all_parser.add_argument("--width", type=int, help="Output viewport width.")
    export_all_parser.add_argument("--height", type=int, help="Output viewport height.")

    export_layout_parser = subparsers.add_parser(
        "export-layout",
        help="Export a human-oriented SVG layout from a YAML diagram definition.",
    )
    export_layout_parser.add_argument("input", type=Path)
    export_layout_parser.add_argument("-o", "--output", type=Path, required=True)
    export_layout_parser.add_argument(
        "--node",
        default="node",
        help="Node.js executable used for layout PNG export. Defaults to node.",
    )
    export_layout_parser.add_argument(
        "--puppeteer-config-file",
        type=Path,
        help="Puppeteer JSON config file used for layout PNG export.",
    )

    return parser


def run_render(args: argparse.Namespace) -> None:
    diagram = load_diagram(args.input)
    write_output(render_mermaid(diagram), args.output)


def run_validate(args: argparse.Namespace) -> None:
    load_diagram(args.input)
    print(f"Valid: {args.input}")


def run_preview(args: argparse.Namespace) -> None:
    diagram = load_diagram(args.input)
    output = render_markdown_preview(diagram, args.input)
    write_output(output, args.output)


def run_export(args: argparse.Namespace) -> None:
    diagram = load_diagram(args.input)
    export_with_mermaid_cli(
        diagram,
        args.output,
        args.mmdc,
        args.puppeteer_config_file,
        args.width,
        args.height,
    )


def run_export_all(args: argparse.Namespace) -> None:
    output_paths = export_directory_with_mermaid_cli(
        args.input_dir,
        args.output_dir,
        args.format,
        args.mmdc,
        args.puppeteer_config_file,
        args.width,
        args.height,
    )
    for output_path in output_paths:
        print(f"Exported: {output_path}")


def run_export_layout(args: argparse.Namespace) -> None:
    diagram = load_diagram(args.input)
    export_layout(diagram, args.output, args.node, args.puppeteer_config_file)


if __name__ == "__main__":
    main()
