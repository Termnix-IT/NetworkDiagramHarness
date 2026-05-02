# YAML Schema

このドキュメントは、Network Diagram Harness が受け取る YAML 定義の仕様です。

現時点では厳密な JSON Schema ファイルではなく、実装とドキュメントの基準になる人間向け仕様として管理します。実装を拡張する場合は、先にこのドキュメントを更新してから parser, renderer, tests を合わせます。

## Top Level

```yaml
title: Web Three Tier Network
direction: LR
zones: []
nodes: []
connections: []
```

| Field | Required | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `title` | no | string | `null` | 図のタイトル。Mermaid ではコメントとして出力します。 |
| `direction` | no | string | `LR` | Mermaid flowchart の向きです。 |
| `zones` | no | array | `[]` | ネットワーク領域やセグメントの一覧です。 |
| `nodes` | no | array | `[]` | サーバ、DB、Firewall などの構成要素です。 |
| `connections` | no | array | `[]` | node 間の接続情報です。 |

## Direction

許可値:

| Value | Meaning |
| --- | --- |
| `LR` | Left to right |
| `RL` | Right to left |
| `TB` | Top to bottom |
| `TD` | Top down |
| `BT` | Bottom to top |

## Zones

`zones` は Mermaid の `subgraph` として出力されます。図の領域分け、ネットワークセグメント、環境境界などを表します。

```yaml
zones:
  - id: dmz
    name: DMZ
    description: Public-facing network segment.
```

| Field | Required | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `id` | yes | string | none | zone の識別子です。node の `zone` から参照されます。 |
| `name` | no | string | `id` | 図に表示する zone 名です。 |
| `description` | no | string | `null` | zone の説明です。現時点では Mermaid 出力には使いません。 |

### Zone Rules

- `zone.id` はファイル内で一意にします。
- `node.zone` から参照される `zone.id` は、必ず `zones` に定義します。
- `zones` の並び順が Mermaid の `subgraph` 出力順になります。

## Nodes

`nodes` は構成図に表示される要素です。

```yaml
nodes:
  - id: web01
    name: Web Server 01
    type: server
    zone: app
    ip: 10.0.10.11
    role: web
    environment: production
    description: Handles web traffic.
```

| Field | Required | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `id` | yes | string | none | node の識別子です。connection の `source` / `target` から参照されます。 |
| `name` | no | string | `id` | 図に表示する node 名です。 |
| `type` | no | string | `server` | node の種類です。Mermaid の shape 選択に使います。 |
| `zone` | no | string | `null` | 所属 zone の `id` です。 |
| `ip` | no | string | `null` | 表示用 IP アドレスです。 |
| `role` | no | string | `null` | node の役割です。 |
| `environment` | no | string | `null` | `production`, `staging` などの環境名です。現時点では Mermaid 出力には使いません。 |
| `description` | no | string | `null` | node の説明です。現時点では Mermaid 出力には使いません。 |

### Node Types

| Type | Mermaid Shape | Intended Meaning |
| --- | --- | --- |
| `external` | rounded | Internet や外部サービス |
| `firewall` | hexagon | Firewall や境界制御 |
| `load_balancer` | rounded | Load balancer |
| `server` | rectangle | Application server や汎用 server |
| `database` | cylinder | Database |
| `network` | parallelogram | Network boundary |
| `subnet` | rectangle | Subnet や segment |

未知の `type` は validation error です。

### Node Label

Mermaid の node label は以下のルールで生成します。

```text
name
name<br/>ip
name<br/>ip / role
name<br/>role
```

`ip` と `role` がどちらも未指定の場合は `name` のみを表示します。

## Connections

`connections` は node 間の接続を表します。

```yaml
connections:
  - source: web01
    target: db01
    protocol: PostgreSQL
    port: 5432
    purpose: application data
    direction: outbound
```

| Field | Required | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `source` | yes | string | none | 接続元 node の `id` です。 |
| `target` | yes | string | none | 接続先 node の `id` です。 |
| `label` | no | string | `null` | 接続ラベルを直接指定します。指定時は `protocol` / `port` / `purpose` より優先します。 |
| `protocol` | no | string | `null` | `HTTPS`, `SSH`, `PostgreSQL` などのプロトコル名です。 |
| `port` | no | number or string | `null` | TCP/UDP port などを表します。 |
| `purpose` | no | string | `null` | 接続目的です。 |
| `direction` | no | string | `outbound` | Mermaid の矢印方向です。 |

### Connection Direction

| Value | Mermaid Arrow | Meaning |
| --- | --- | --- |
| `outbound` | `source --> target` | source から target への接続 |
| `inbound` | `source <-- target` | target から source への接続として表示 |
| `bidirectional` | `source <--> target` | 双方向接続 |

### Connection Label

`label` がある場合:

```yaml
label: HTTPS 443
```

出力:

```mermaid
source -->|"HTTPS 443"| target
```

`label` がない場合は、`protocol`, `port`, `purpose` をこの順序で結合します。

```yaml
protocol: HTTPS
port: 443
purpose: public access
```

出力:

```mermaid
source -->|"HTTPS / 443 / public access"| target
```

### Port Rules

- `port` は `1` から `65535` の数値を許可します。
- `port` は `1000-2000` のような範囲文字列も許可します。
- 範囲指定は開始値が終了値以下である必要があります。
- `0`, `65536`, `9000-8000` は invalid です。

### Protocol Rules

- `protocol` は英字から始めます。
- `protocol` に使える文字は英数字、`+`, `.`, `_`, `-` です。
- 空白を含む値は invalid です。
- 例: `HTTPS`, `SSH`, `PostgreSQL`, `TCP`, `UDP`, `gRPC`, `HTTP-API`

## Validation Rules

現時点の parser は以下を検証します。

- `direction` は `TB`, `TD`, `BT`, `RL`, `LR` のみ許可
- `zone.id` の重複はエラー
- `node.id` の重複はエラー
- `node.zone` は既存 `zone.id` のみ許可
- `connection.source` と `connection.target` は既存 `node.id` のみ許可
- `node.type` は定義済み type のみ許可
- `node.ip` は有効な IP アドレスのみ許可
- `connection.port` は有効な port 番号または port 範囲のみ許可
- `connection.protocol` は protocol 文字列ルールに従う値のみ許可
- `connection.direction` は `outbound`, `inbound`, `bidirectional` のみ許可
- `examples/` 配下の YAML は全て parse 可能であること
- `examples/` 配下の IP アドレスは public-looking な実 IP を避けること

## Public Example Rules

`examples/` と `docs/` に入れる YAML / Mermaid は、GitHub 公開できる架空データだけにします。

入れてよいもの:

- 架空の server 名
- RFC 5737 の documentation 用 IP アドレス
  - `192.0.2.0/24`
  - `198.51.100.0/24`
  - `203.0.113.0/24`
- 実構成に紐づかない private IP 例
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`
- 一般的な protocol / port 例

入れないもの:

- 実サーバ名
- 実 IP アドレス
- 実ドメイン名
- 社内 subnet / VLAN / VPN / Firewall rule
- cloud account ID / project ID / resource ID
- 実構成から生成した Mermaid や画像

実構成は Git 管理外の `private/` または `local/` に置きます。

## Minimal Example

```yaml
title: Minimal Network
direction: LR

nodes:
  - id: internet
    name: Internet
    type: external

  - id: web
    name: Web Server
    type: server

connections:
  - source: internet
    target: web
    protocol: HTTPS
    port: 443
```

## Zoned Example

```yaml
title: Zoned Network
direction: LR

zones:
  - id: dmz
    name: DMZ

  - id: app
    name: Application Segment

nodes:
  - id: lb01
    name: Load Balancer
    type: load_balancer
    zone: dmz
    ip: 10.0.1.10

  - id: web01
    name: Web Server 01
    type: server
    zone: app
    ip: 10.0.10.11
    role: web

connections:
  - source: lb01
    target: web01
    protocol: HTTP
    port: 8080
    purpose: application traffic
```

## Reserved For Future Expansion

以下は候補ですが、まだ正式仕様ではありません。

- top-level `metadata`
- top-level `tags`
- `owners`
- protocol allowlist
- IP address classification
- output profiles
- JSON Schema export

## Mermaid Styling

Mermaid 出力では、使用された node type ごとに `classDef` と `class` を出力します。

例:

```mermaid
classDef type_server fill:#ede9fe,stroke:#6d28d9,color:#111827
class web01,web02 type_server
```

現時点の色は renderer 側の固定値です。YAML から style を指定する仕組みはまだ正式仕様ではありません。

## Image Export

画像出力は YAML schema ではなく CLI の責務です。

```powershell
network-diagram-harness export examples/web-three-tier.yml --output output/web-three-tier.svg
```

`export` は Mermaid CLI の `mmdc` を呼び出します。対応拡張子は `.svg`, `.png`, `.pdf` です。
