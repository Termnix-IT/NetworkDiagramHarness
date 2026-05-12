# Folder Structure

このドキュメントは、Network Diagram Harness のフォルダ構造と各ディレクトリの役割を整理したものです。

## Overview

```text
.
├── .github/
│   └── workflows/
├── docs/
│   ├── examples/
│   ├── concept.md
│   ├── current-state.md
│   ├── folder-structure.md
│   ├── image-export-workflow.md
│   ├── prompt-workflow.md
│   ├── profile-network-workflow.md
│   ├── schema.md
│   └── specification.md
├── examples/
├── prompts/
├── scripts/
├── src/
│   └── network_diagram_harness/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── README.md
└── SECURITY.md
```

## Managed Directories

Git 管理する公開対象のディレクトリです。

| Path | Role |
| --- | --- |
| `.github/workflows/` | GitHub Actions の CI 設定です。 |
| `docs/` | 設計、運用、スキーマ、画像出力などのドキュメントです。 |
| `docs/examples/` | `examples/*.yml` から生成した Markdown preview です。 |
| `examples/` | 公開可能な架空ネットワーク構成 YAML です。 |
| `prompts/` | Codex へ依頼するときのプロンプト雛形です。 |
| `scripts/` | ローカル運用や画像出力の補助スクリプトです。 |
| `src/network_diagram_harness/` | ハーネス本体の Python パッケージです。 |
| `tests/` | pytest によるテストです。 |

## Root Files

| Path | Role |
| --- | --- |
| `README.md` | プロジェクト概要と基本的な使い方です。 |
| `pyproject.toml` | Python package metadata、依存関係、pytest 設定です。 |
| `LICENSE` | ライセンスです。 |
| `CHANGELOG.md` | 変更履歴です。 |
| `CONTRIBUTING.md` | contribution と公開データの注意点です。 |
| `SECURITY.md` | セキュリティと実構成データの扱いです。 |
| `.gitignore` | 生成物、仮想環境、private/local データの除外設定です。 |

## Source Package

```text
src/network_diagram_harness/
├── __init__.py
├── cli.py
├── export.py
├── io.py
├── mermaid.py
├── model.py
└── preview.py
```

| Path | Role |
| --- | --- |
| `cli.py` | `network-diagram-harness` CLI の entry point です。 |
| `model.py` | YAML から内部モデルを作り、validation を行います。 |
| `mermaid.py` | 内部モデルから Mermaid flowchart を生成します。 |
| `preview.py` | Mermaid code block を含む Markdown preview を生成します。 |
| `export.py` | Mermaid CLI を使って SVG/PNG/PDF を出力します。 |
| `io.py` | YAML 読み込みとファイル出力の共通処理です。 |

## Public Examples

```text
examples/
├── multi-zone-network.yml
├── office-and-cloud.yml
├── profile-home-lab.yml
├── simple-network.yml
├── web-three-tier.yml
└── zero-trust-access.yml
```

`examples/` には公開可能な架空データだけを置きます。実サーバ名、実 IP アドレス、社内ドメイン、実 subnet/VLAN/VPN/firewall rule は入れません。

対応する Markdown preview は `docs/examples/` に置きます。

```text
docs/examples/
├── multi-zone-network.md
├── office-and-cloud.md
├── profile-home-lab.md
├── simple-network.md
├── web-three-tier.md
└── zero-trust-access.md
```

## Scripts

```text
scripts/
└── export-profile-images.ps1
```

| Path | Role |
| --- | --- |
| `scripts/export-profile-images.ps1` | 自宅ネットワーク構成図の自分向け・公開向け画像をまとめて出力します。 |

## Local And Private Directories

以下は Git 管理しないローカル専用ディレクトリです。

```text
local/
private/
output/
workspaces/
```

| Path | Role |
| --- | --- |
| `local/` | ローカル検証用の YAML を置きます。例: `local/test-network.local.yml` |
| `private/` | 実構成や公開したくない構成を置きます。 |
| `output/` | Mermaid、Markdown preview、SVG/PNG/PDF などの生成物を置きます。 |
| `workspaces/` | 将来的な作業用領域です。 |

## Temporary Directories

以下はツール実行時の一時ファイルやキャッシュです。Git 管理しません。

```text
.venv/
.tmp/
.tmp-tests/
pip-cache/
pytest-cache-files-*/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
```

## Data Placement Rules

| Data | Put In | Git Managed |
| --- | --- | --- |
| 公開できる架空サンプル | `examples/` | yes |
| サンプルの Markdown preview | `docs/examples/` | yes |
| ローカル検証用 YAML | `local/` | no |
| 実構成 YAML | `private/` | no |
| Mermaid / Markdown / 画像生成物 | `output/` | no |
| Codex 依頼テンプレート | `prompts/` | yes |

## Common Workflow Paths

自然文からローカル構成図を作る場合:

```text
local/<name>.local.yml
  -> output/<name>.md
  -> output/images/<name>.svg
```

公開サンプルを追加する場合:

```text
examples/<name>.yml
  -> docs/examples/<name>.md
```

## Related Docs

- [prompt-workflow.md](prompt-workflow.md)
- [profile-network-workflow.md](profile-network-workflow.md)
- [image-export-workflow.md](image-export-workflow.md)
- [schema.md](schema.md)
- [current-state.md](current-state.md)
- [specification.md](specification.md)
