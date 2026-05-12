# 自宅ネットワーク・クラウド構成

## Source

`examples/profile-home-lab.yml`

## Summary

- Zones: `5`
- Nodes: `12`
- Connections: `12`

## Mermaid Preview

```mermaid
flowchart TB
  %% 自宅ネットワーク・クラウド構成
  subgraph zone_internet["インターネット"]
    internet(["インターネット"])
    isp_edge(["回線接続<br/>光回線 / 動的DNS"])
  end
  subgraph zone_home_edge["自宅エッジ"]
    edge_router{"エッジルーター<br/>NAT / Firewall / 自宅境界"}
  end
  subgraph zone_dmz["自宅ラボサービス"]
    lab_service_host["ラボ用サーバー<br/>自宅内サービス"]
  end
  subgraph zone_internal["内部セグメント"]
    internal_router{"内部ルーター<br/>VLAN / ACL / 監視"}
    client_segment["クライアント<br/>日常利用端末"]
    server_segment["サーバー<br/>ラボ用途"]
    wifi_segment["Wi-Fi<br/>無線端末"]
    test_segment["検証環境<br/>分離テスト"]
    monitoring_server["監視サーバー<br/>メトリクス / ファイル共有"]
  end
  subgraph zone_cloud["クラウド公開基盤"]
    cdn(["CDN<br/>公開サイト配信"])
    object_storage[("オブジェクトストレージ<br/>静的サイト配信元")]
  end
  internet -->|"光回線"| isp_edge
  isp_edge -->|"WAN"| edge_router
  edge_router -->|"ラボ接続"| lab_service_host
  edge_router -->|"内部接続"| internal_router
  internal_router -->|"クライアントVLAN"| client_segment
  internal_router -->|"サーバーVLAN"| server_segment
  internal_router -->|"Wi-Fi VLAN"| wifi_segment
  internal_router -->|"検証VLAN"| test_segment
  monitoring_server -->|"ネットワーク監視"| internal_router
  monitoring_server -->|"ホスト監視"| lab_service_host
  internet -->|"HTTPS 443 公開サイト"| cdn
  cdn -->|"オリジン"| object_storage
  classDef type_database fill:#fef3c7,stroke:#b45309,color:#111827
  classDef type_external fill:#e0f2fe,stroke:#0369a1,color:#111827
  classDef type_firewall fill:#fee2e2,stroke:#b91c1c,color:#111827
  classDef type_load_balancer fill:#dcfce7,stroke:#15803d,color:#111827
  classDef type_server fill:#ede9fe,stroke:#6d28d9,color:#111827
  classDef type_subnet fill:#ecfeff,stroke:#0e7490,color:#111827
  class object_storage type_database
  class internet,isp_edge type_external
  class edge_router,internal_router type_firewall
  class cdn type_load_balancer
  class lab_service_host,monitoring_server type_server
  class client_segment,server_segment,wifi_segment,test_segment type_subnet
```
