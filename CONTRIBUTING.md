# Contributing

Contributions are welcome, but this repository is designed to remain safe for public use.

## Public Data Rule

Do not commit real infrastructure data.

Avoid:

- real server names
- real IP addresses
- real domains
- VPN, VLAN, subnet, firewall, or routing details from an actual environment
- cloud account IDs, project IDs, resource IDs, or tenant IDs
- generated diagrams from real environments

Use only fictional examples or documentation ranges in `examples/` and `docs/`.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
python -m pytest
```

## Updating Examples

When adding or changing `examples/*.yml`, regenerate the Markdown preview:

```powershell
network-diagram-harness preview examples/web-three-tier.yml --output docs/examples/web-three-tier.md
```

Run tests before submitting changes:

```powershell
python -m pytest
```
