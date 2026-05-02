# Specification

このドキュメントは、Network Diagram Harness の全体仕様です。

YAML 入力の詳細は [schema.md](schema.md)、プロンプト運用は [prompt-workflow.md](prompt-workflow.md)、画像出力は [image-export-workflow.md](image-export-workflow.md)、フォルダ構造は [folder-structure.md](folder-structure.md) を参照します。

## Purpose

Network Diagram Harness は、ネットワーク・サーバ構成図を構造化された YAML から生成するためのハーネスです。

目的:

- 自然文で伝えた構成を YAML に落とし込む
- YAML を構成図の正本として扱う
- Mermaid preview で確認できるようにする
- 必要に応じて SVG/PNG/PDF に画像出力する
- 公開可能なサンプルと実構成データを明確に分離する

## Scope

対象:

- ネットワーク構成図
- サーバ構成図
- zone / segment 単位のグルーピング
- node 間の通信経路
- Mermaid Markdown preview
- Mermaid CLI を使った画像出力

対象外:

- 実ネットワークへの疎通確認
- パケットキャプチャ
- クラウド API からの自動収集
- GUI エディタ
- 手編集した draw.io ファイルの再取り込み
- Mermaid CLI なしでの SVG/PNG/PDF 生成

## Source Of Truth

このハーネスでは YAML を正本とします。

```text
YAML
  -> validate
  -> Mermaid
  -> Markdown preview
  -> SVG / PNG / PDF
```

Mermaid、Markdown、画像ファイルは生成物です。実構成を編集する場合も、画像や Markdown ではなく YAML を更新します。

## Inputs

主入力は YAML ファイルです。

```text
examples/*.yml
local/*.local.yml
private/*.private.yml
```

YAML は主に以下の要素を持ちます。

- `title`
- `direction`
- `zones`
- `nodes`
- `connections`

詳細な YAML 仕様は [schema.md](schema.md) に定義します。

## Outputs

出力形式:

| Output | Command | Purpose |
| --- | --- | --- |
| Mermaid | `render` | Mermaid 単体の確認や外部利用 |
| Markdown preview | `preview` | Mermaid code block を含むレビュー用 Markdown |
| SVG | `export` / `export-all` | ドキュメント貼り付けやレビュー用画像 |
| PNG | `export` / `export-all` | 画像としての共有用 |
| PDF | `export` / `export-all` | 固定レイアウトの配布用 |

出力先の標準:

```text
output/
output/images/
docs/examples/
```

`output/` は Git 管理しません。`docs/examples/` は公開サンプル用の Markdown preview として Git 管理します。

## Processing Flow

通常の処理フロー:

```text
user prompt
  -> Codex creates YAML
  -> network-diagram-harness validate
  -> network-diagram-harness preview
  -> user reviews Markdown preview
  -> network-diagram-harness export
```

内部処理:

```text
YAML file
  -> io.load_diagram
  -> model.parse_diagram
  -> model.validate_diagram
  -> mermaid.render_mermaid
  -> preview.render_markdown_preview
  -> export.export_with_mermaid_cli
```

## CLI Commands

| Command | Description |
| --- | --- |
| `render` | YAML から Mermaid を生成します。 |
| `validate` | YAML の validation のみ実行します。 |
| `preview` | Mermaid code block を埋め込んだ Markdown を生成します。 |
| `export` | 単一 YAML を SVG/PNG/PDF に出力します。 |
| `export-all` | ディレクトリ配下の `*.yml` をまとめて画像出力します。 |

後方互換:

```powershell
network-diagram-harness examples/simple-network.yml
```

これは `render` と同じ動作です。

## Validation Rules

Validation は `model.py` が担当します。

検証対象:

- `direction` の許可値
- `zone.id` の重複
- `node.id` の重複
- `node.zone` の参照整合性
- `node.type` の許可値
- `node.ip` の IP アドレス形式
- `connection.source` / `connection.target` の参照整合性
- `connection.port` の範囲
- `connection.protocol` の形式
- `connection.direction` の許可値

Validation error は CLI で traceback ではなく、短い `error: ...` として表示します。

## Mermaid Rendering Rules

Mermaid rendering は `mermaid.py` が担当します。

主な規則:

- `direction` は `flowchart <direction>` に反映する
- `zones` は `subgraph` として出力する
- subgraph ID は node ID と衝突しないように `zone_<id>` を使う
- `node.type` ごとに shape を変える
- `node.ip` と `node.role` は node label に表示する
- `connection.label` があればそれを優先する
- `label` がなければ `protocol / port / purpose` から接続ラベルを作る
- 使用された `node.type` ごとに `classDef` と `class` を出力する

## Image Export Rules

画像出力は `export.py` が担当します。

対応形式:

- `.svg`
- `.png`
- `.pdf`

画像出力には Mermaid CLI の `mmdc` が必要です。

単一出力:

```powershell
network-diagram-harness export local/test-network.local.yml --output output/images/test-network.svg
```

一括出力:

```powershell
network-diagram-harness export-all local --output-dir output/images --format svg
```

`mmdc` がない環境では `validate`, `render`, `preview` は利用可能です。

## File Placement Rules

公開対象:

```text
examples/
docs/
docs/examples/
prompts/
src/
tests/
```

非公開・ローカル対象:

```text
local/
private/
output/
workspaces/
```

配置ルール:

| Data | Put In | Git Managed |
| --- | --- | --- |
| 公開できる架空サンプル | `examples/` | yes |
| 公開サンプルの preview | `docs/examples/` | yes |
| ローカル検証用 YAML | `local/` | no |
| 実構成 YAML | `private/` | no |
| 生成物 | `output/` | no |
| Codex 依頼テンプレート | `prompts/` | yes |

詳細は [folder-structure.md](folder-structure.md) に定義します。

## Public And Private Data Policy

公開リポジトリには、公開できる架空構成だけを入れます。

公開してよいもの:

- 架空の server 名
- documentation 用 IP
- 一般的な private IP 例
- 一般的な protocol / port 例

公開しないもの:

- 実サーバ名
- 実 IP アドレス
- 実ドメイン名
- 社内 subnet / VLAN / VPN / firewall rule
- cloud account ID / project ID / resource ID
- 実構成から生成した Mermaid、Markdown、画像

実構成は `local/` または `private/` に置き、Git 管理しません。

## Prompt-Based Operation

Codex に自然文で構成を伝える運用をサポートします。

標準依頼:

```text
以下の構成で network diagram harness 用の YAML を作成してください。
まず Mermaid preview の Markdown まで生成してください。
```

Codex は以下を行います。

1. 構成を `zones`, `nodes`, `connections` に分解する
2. `local/<name>.local.yml` を作成する
3. `validate` を実行する
4. エラーがあれば YAML を修正する
5. `preview` を実行する
6. `output/<name>.md` を報告する
7. 問題なければ `export` で画像化する

詳細は [prompt-workflow.md](prompt-workflow.md) に定義します。

## Error Handling

CLI は以下の方針でエラーを扱います。

- validation error は `error: <message>` として表示する
- unsupported format は `error: Unsupported export format...` として表示する
- Mermaid CLI 未導入時は `error: Mermaid CLI executable was not found...` として表示する
- 想定内エラーでは traceback を表示しない

## Testing Requirements

pytest で以下を確認します。

- renderer の出力
- validation error
- CLI command
- Markdown preview
- image export command
- public example YAML の parse
- public example に実 IP らしい値が混ざらないこと
- docs にローカル絶対パスが混ざらないこと
- `docs/examples/*.md` が各 `examples/*.yml` に対応して存在すること

## Current Limitations

- Mermaid CLI がない場合、画像出力はできない
- draw.io 形式は未実装
- 自動レイアウトは Mermaid に依存する
- YAML からの生成が一方向で、画像や draw.io から YAML へ戻す機能はない
- protocol allowlist は未実装
- JSON Schema export は未実装

## Future Extensions

候補:

- draw.io XML export
- PlantUML export
- JSON Schema export
- protocol allowlist
- IP address classification
- output profiles
- style profiles
- CI での preview 再生成チェック
