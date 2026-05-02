# Concept

## Purpose

Network Diagram Harness は、ネットワーク・サーバ構成図をコードとして扱うためのハーネスです。

従来の構成図は、手作業で作成されることが多く、以下の問題が起きやすくなります。

- 実際の構成と図面がずれる
- 図面の表記ルールが担当者ごとに変わる
- 差分レビューが難しい
- 既存図面の再利用や自動更新が難しい

このリポジトリでは、構成定義を入力として、図面を生成する流れを標準化します。

## Core Flow

```text
infrastructure definition
  -> validation
  -> diagram model
  -> renderer
  -> diagram output
```

最初の実装では、以下の流れにします。

```text
YAML
  -> Python model
  -> Mermaid renderer
  -> .mmd
```

## Design Principles

- 定義ファイルを Git でレビューしやすくする
- 図面の見た目より、構成情報の一貫性を優先する
- 出力形式は差し替え可能にする
- 最初は小さく動く CLI にする
- 将来的な lint や CI 利用を前提にする

## Non Goals For MVP

MVP では以下を対象外にします。

- 実ネットワークへの疎通確認
- パケットキャプチャや通信テスト
- クラウド API からの自動収集
- GUI エディタ
- 高度なレイアウト最適化

## Future Ideas

- AWS/Azure/GCP のリソース定義からの取り込み
- Terraform state からの構成図生成
- draw.io XML への出力
- PlantUML への出力
- Markdown ドキュメントへの埋め込み
- diagram lint による命名規則や接続ルールの検証
