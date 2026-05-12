# Layout Workflow

このドキュメントは、人間が見やすい掲載向け構成図を生成するための layout 出力手順です。

## Purpose

Mermaid は構成確認や Markdown preview には便利ですが、配置は自動レイアウトに依存します。経歴ページや公開ページに載せる図では、Internet、Cloud、Edge、DMZ、Internal、VLAN などの位置関係を人間が読みやすい形に固定したい場合があります。

その用途には `export-layout` を使います。

```text
YAML
  -> validate
  -> export-layout
  -> SVG
```

## YAML

掲載向け layout を使う YAML には `layout.profile` を指定します。

```yaml
layout:
  profile: home_lab
```

`home_lab` profile は、自宅ネットワークや home lab の構成図向けに、以下の領域を固定配置します。

| Area | Placement |
| --- | --- |
| Internet | 上部中央 |
| Cloud / AWS | 左側 |
| Home Edge | 右上 |
| DMZ / Home Lab Service Zone | 右下 |
| Internal Network | 中央下 |
| VLAN / subnet | Internal Network 下部 |

## Export

公開向け SVG:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-layout examples/profile-home-lab.yml --output output/images/public/profile-home-lab-layout.svg
```

自分向け SVG:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-layout local/home-network.local.yml --output output/images/private/home-network-layout.svg
```

## Role Split

| Output | Role |
| --- | --- |
| `preview` | Markdown 上で Mermaid を確認するための出力 |
| `render` | Mermaid source を確認・保存するための出力 |
| `export` | Mermaid CLI で SVG / PNG / PDF に変換する出力 |
| `export-layout` | 掲載向けの固定配置 SVG 出力 |

## Current Limitations

- `export-layout` は現時点では `.svg` のみ対応します。
- `home_lab` profile は固定テンプレートです。任意座標指定や複数 layout profile は今後の拡張候補です。
- PNG が必要な場合は、生成した SVG を別ツールで PNG に変換します。
