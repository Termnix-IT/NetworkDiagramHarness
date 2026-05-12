# Profile Network Workflow

このドキュメントは、自宅ネットワーク・サーバ環境の構成図を「自分向け」と「公開向け」に分けて育てるための運用手順です。

## File Roles

| Path | Role | Git Managed |
| --- | --- | --- |
| `private/home-network/reference/` | 元画像、メモ、公開しない参考資料 | no |
| `local/home-network.local.yml` | 実構成を反映する自分向け YAML | no |
| `output/home-network.md` | 自分向け Markdown preview | no |
| `output/home-network.mmd` | 自分向け Mermaid | no |
| `examples/profile-home-lab.yml` | 経歴ページなどに使う公開向け YAML | yes |
| `docs/examples/profile-home-lab.md` | 公開向け Markdown preview | yes |
| `output/images/private/home-network.png` | 自分向け画像出力 | no |
| `output/images/public/profile-home-lab.png` | 公開向け画像出力 | no |
| `scripts/export-profile-images.ps1` | 自分向け・公開向け画像の一括出力 | yes |

## Update Flow

自宅環境を変更したら、まず実構成側を更新します。

```powershell
.\.venv\Scripts\network-diagram-harness.exe validate local/home-network.local.yml
.\.venv\Scripts\network-diagram-harness.exe preview local/home-network.local.yml --output output/home-network.md
.\.venv\Scripts\network-diagram-harness.exe render local/home-network.local.yml --output output/home-network.mmd
```

次に、公開してよい粒度に抽象化して `examples/profile-home-lab.yml` を更新します。

```powershell
.\.venv\Scripts\network-diagram-harness.exe validate examples/profile-home-lab.yml
.\.venv\Scripts\network-diagram-harness.exe preview examples/profile-home-lab.yml --output docs/examples/profile-home-lab.md
```

Mermaid CLI が使える環境では、経歴ページ掲載用の画像を出力します。

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/profile-home-lab.yml --output output/images/public/profile-home-lab.svg
```

## Profile Image Export

自分向けと公開向けをまとめて更新する場合は、専用スクリプトを使います。

```powershell
.\scripts\export-profile-images.ps1
```

既定では PNG を出力します。

```text
output/images/private/home-network.png
output/images/public/profile-home-lab.png
```

既定の画像サイズは `1400x1000` です。サイズを変える場合は `-Width` と `-Height` を指定します。

```powershell
.\scripts\export-profile-images.ps1 -Width 1600 -Height 1200
```

SVG や PDF が必要な場合は `-Format` を指定します。

```powershell
.\scripts\export-profile-images.ps1 -Format svg
.\scripts\export-profile-images.ps1 -Format pdf
```

`mmdc` が PATH にない場合は、Mermaid CLI のパスを指定します。

```powershell
.\scripts\export-profile-images.ps1 -Format png -Mmdc C:\path\to\mmdc.cmd
```

Mermaid CLI のブラウザ起動設定は `scripts/puppeteer-config.json` を使います。別の設定を使う場合は `-PuppeteerConfigFile` を指定します。

画像出力環境がまだない状態で YAML、Markdown preview、Mermaid だけを更新する場合は、`-SkipImageExport` を使います。

```powershell
.\scripts\export-profile-images.ps1 -SkipImageExport
```

## Public Sanitizing Rules

公開向け YAML には、以下を入れません。

- 実 DDNS 名、実ドメイン名、実 CloudFront domain
- 実 bucket 名、account ID、resource ID
- 実サーバ名、実端末名
- 実 IP アドレス、実 subnet、実 VLAN ID
- 管理用ポートや遠隔管理ツールなど、攻撃面の推測につながる詳細

公開向けには、次のように抽象化します。

| Private Detail | Public Expression |
| --- | --- |
| `192.168.x.x` の実 IP | `Client Segment`, `Server Segment` |
| 実 DDNS domain | `dynamic DNS` |
| 実 CloudFront domain | `CDN` |
| 実 S3 bucket | `Object Storage` |
| 具体的な管理ツール | `monitoring`, `remote administration` |
| 詳細な port forwarding | `home lab access` |

## Review Checklist

公開前に以下を確認します。

- `examples/profile-home-lab.yml` に実名や実識別子が入っていない
- `docs/examples/profile-home-lab.md` が最新 YAML から再生成されている
- 経歴ページに載せる画像が `examples/profile-home-lab.yml` から生成されている
- 自分向けの詳細は `local/` または `private/` に残している
