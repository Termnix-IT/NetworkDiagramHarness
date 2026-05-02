# Network Diagram Request Prompt

以下の構成を network diagram harness 用の YAML にしてください。

## Output

- YAML:
- Preview:

## Purpose

-

## Zones

-

## Nodes

形式:

```text
- <name>, type=<type>, zone=<zone>, ip=<ip>, role=<role>
```

nodes:

-

## Connections

形式:

```text
- <source> -> <target>, protocol=<protocol>, port=<port>, purpose=<purpose>
```

connections:

-

## Requirements

- 実構成の場合は `local/` または `private/` に YAML を作成する
- 公開サンプルの場合だけ `examples/` に作成する
- 作成後に `validate` を実行する
- validation error があれば修正する
- 最後に `preview` を生成する
- 出力ファイルの場所を報告する
