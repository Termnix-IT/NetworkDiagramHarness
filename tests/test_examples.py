from ipaddress import ip_address
from pathlib import Path

import yaml

from network_diagram_harness.model import parse_diagram


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
DOC_EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "docs" / "examples"


def test_all_examples_are_valid() -> None:
    for path in EXAMPLES_DIR.glob("*.yml"):
        with path.open("r", encoding="utf-8") as file:
            parse_diagram(yaml.safe_load(file) or {})


def test_public_examples_do_not_use_real_public_ips() -> None:
    for path in EXAMPLES_DIR.glob("*.yml"):
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

        for node in data.get("nodes", []):
            value = node.get("ip")
            if not value:
                continue

            parsed = ip_address(str(value))
            assert (
                parsed.is_private or parsed.is_loopback or parsed.is_link_local
            ), f"{path.name} contains a public-looking IP address: {value}"


def test_each_example_has_markdown_preview() -> None:
    for path in EXAMPLES_DIR.glob("*.yml"):
        preview_path = DOC_EXAMPLES_DIR / f"{path.stem}.md"
        assert preview_path.exists(), f"Missing preview: {preview_path}"
        content = preview_path.read_text(encoding="utf-8")
        assert f"`examples/{path.name}`" in content
        assert "```mermaid" in content
