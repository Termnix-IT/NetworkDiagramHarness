# Image Export Workflow

このドキュメントは、YAML から Mermaid を経由して SVG/PNG/PDF を生成する画像出力ハーネスの使い方です。

## Requirements

画像出力には Mermaid CLI の `mmdc` が必要です。

```powershell
npm install -g @mermaid-js/mermaid-cli
```

`mmdc` が使えない環境でも、以下は利用できます。

```powershell
.\.venv\Scripts\network-diagram-harness.exe validate examples/web-three-tier.yml
.\.venv\Scripts\network-diagram-harness.exe preview examples/web-three-tier.yml --output output/web-three-tier.md
```

## Single Diagram Export

SVG:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.svg
```

PNG:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.png
```

読みやすい大きさで PNG を出す場合:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.png --width 1400 --height 1000
```

PDF:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.pdf
```

## Batch Export

`examples/` 配下の全 YAML を SVG にします。

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-all examples --output-dir output/images --format svg
```

ローカル検証用の全 YAML を PNG にします。

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-all local --output-dir output/local-images --format png
```

## Profile Image Export

自宅ネットワーク構成図は、自分向けと公開向けを分けて画像出力します。

```powershell
.\scripts\export-profile-images.ps1
```

既定では以下の PNG を生成します。

```text
output/images/private/home-network.png
output/images/public/profile-home-lab.png
output/images/private/home-network-layout.svg
output/images/public/profile-home-lab-layout.svg
output/images/private/home-network-layout.png
output/images/public/profile-home-lab-layout.png
```

専用スクリプトは既定で `1400x1000` の PNG と、掲載向け固定配置 SVG を生成します。PNG 生成では `scripts/puppeteer-config.json` を使って Mermaid CLI のブラウザ起動を安定させます。

SVG や PDF で出力する場合:

```powershell
.\scripts\export-profile-images.ps1 -Format svg
.\scripts\export-profile-images.ps1 -Format pdf
```

サイズを変える場合:

```powershell
.\scripts\export-profile-images.ps1 -Width 1600 -Height 1200
```

画像出力には `mmdc` が必要です。`mmdc` がまだ使えない場合でも、以下で YAML validation、Markdown preview、Mermaid 生成だけを更新できます。

```powershell
.\scripts\export-profile-images.ps1 -SkipImageExport
```

## Custom Mermaid CLI Path

`mmdc` が PATH にない場合は、`--mmdc` で指定できます。

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.svg --mmdc C:\path\to\mmdc.cmd
```

Puppeteer 設定を指定する場合:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.png --puppeteer-config-file scripts/puppeteer-config.json
```

## Recommended Harness Flow

```text
YAML
  -> validate
  -> preview
  -> review Markdown Mermaid preview
  -> export SVG/PNG/PDF
```

最初から画像だけを見るのではなく、まず Markdown preview で構成を確認してから画像化します。

## Human-Oriented Layout Export

Mermaid の自動レイアウトではなく、人間が見やすい固定配置 SVG を出す場合は `export-layout` を使います。

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-layout examples/profile-home-lab.yml --output output/images/public/profile-home-lab-layout.svg
```

PNG で出す場合:

```powershell
.\.venv\Scripts\network-diagram-harness.exe export-layout examples/profile-home-lab.yml --output output/images/public/profile-home-lab-layout.png --puppeteer-config-file scripts/puppeteer-config.json
```

詳細は [layout-workflow.md](layout-workflow.md) にまとめています。
