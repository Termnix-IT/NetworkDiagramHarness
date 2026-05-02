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

## Custom Mermaid CLI Path

`mmdc` が PATH にない場合は、`--mmdc` で指定できます。

```powershell
.\.venv\Scripts\network-diagram-harness.exe export examples/web-three-tier.yml --output output/images/web-three-tier.svg --mmdc C:\path\to\mmdc.cmd
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
