# Prompt Workflow

このドキュメントは、Codex に自然文でネットワーク・サーバ構成を伝え、このハーネスで YAML 化、検証、Markdown preview 生成まで行うための運用手順です。

## Basic Flow

```text
user prompt
  -> Codex creates YAML
  -> harness validate
  -> harness preview
  -> user reviews Mermaid preview
  -> Codex updates YAML if needed
```

## Where To Put Files

公開可能な架空サンプル:

```text
examples/
docs/examples/
```

ローカル検証用:

```text
local/
output/
```

実構成や公開したくない構成:

```text
private/
output/
```

`local/`, `private/`, `output/` は Git 管理外です。

## Request Template

Codex に依頼するときは、次の情報を渡すと安定します。

```text
以下の構成を network diagram harness 用の YAML にしてください。

目的:
- <何の構成図か>

出力先:
- YAML: local/<name>.local.yml
- Preview: output/<name>.md

zones:
- <zone name>

nodes:
- <node name>, type=<type>, zone=<zone>, ip=<ip>, role=<role>

connections:
- <source> -> <target>, protocol=<protocol>, port=<port>, purpose=<purpose>

作成後に以下を実行してください。
- validate
- preview
```

## Example Request

```text
以下の構成を network diagram harness 用の YAML にしてください。

目的:
- Web three-tier 構成の検証

出力先:
- YAML: local/web-three-tier.local.yml
- Preview: output/web-three-tier.md

zones:
- Internet
- DMZ
- Application Segment
- Database Segment
- Management Segment

nodes:
- Internet, type=external, zone=Internet
- Edge Firewall, type=firewall, zone=DMZ, ip=203.0.113.10
- Load Balancer, type=load_balancer, zone=DMZ, ip=10.0.1.10, role=public ingress
- Web Server 01, type=server, zone=Application Segment, ip=10.0.10.11, role=web
- Web Server 02, type=server, zone=Application Segment, ip=10.0.10.12, role=web
- Primary Database, type=database, zone=Database Segment, ip=10.0.20.11, role=primary
- Bastion Host, type=server, zone=Management Segment, ip=10.0.99.10, role=admin entrypoint

connections:
- Internet -> Edge Firewall, protocol=HTTPS, port=443, purpose=public access
- Edge Firewall -> Load Balancer, protocol=HTTPS, port=443, purpose=ingress filtering
- Load Balancer -> Web Server 01, protocol=HTTP, port=8080, purpose=application traffic
- Load Balancer -> Web Server 02, protocol=HTTP, port=8080, purpose=application traffic
- Web Server 01 -> Primary Database, protocol=PostgreSQL, port=5432, purpose=application data
- Web Server 02 -> Primary Database, protocol=PostgreSQL, port=5432, purpose=application data
- Bastion Host -> Web Server 01, protocol=SSH, port=22, purpose=administration
- Bastion Host -> Web Server 02, protocol=SSH, port=22, purpose=administration

作成後に validate と preview を実行してください。
```

## Commands Codex Should Run

```powershell
.\.venv\Scripts\network-diagram-harness.exe validate local/<name>.local.yml
```

```powershell
.\.venv\Scripts\network-diagram-harness.exe preview local/<name>.local.yml --output output/<name>.md
```

Mermaid だけを生成する場合:

```powershell
.\.venv\Scripts\network-diagram-harness.exe render local/<name>.local.yml --output output/<name>.mmd
```

Mermaid CLI が使える場合:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export local/<name>.local.yml --output output/<name>.svg
```

複数ファイルをまとめて画像化する場合:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-all local --output-dir output/images --format svg
```

## Codex Operating Rules

Codex は以下の順序で作業します。

1. 依頼内容から `zones`, `nodes`, `connections` を抽出する
2. 不足情報があっても合理的に補完できる場合は仮の値で進める
3. 実構成らしい情報は `examples/` に置かない
4. 指定がなければ `local/<name>.local.yml` に作る
5. `validate` を実行する
6. validation error があれば YAML を修正する
7. `preview` を実行する
8. 出力 Markdown の場所を報告する

## Review Points

Preview を見て確認する点:

- zone の分け方が意図通りか
- node の type が適切か
- 接続方向が正しいか
- protocol / port / purpose が読みやすいか
- 実データを公開側に置いていないか
