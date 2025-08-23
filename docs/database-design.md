# データベース設計書

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **データベース**: Amazon DynamoDB
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

---

##  設計方針

### DynamoDB選定理由
1. **サーバーレス**: インフラ管理不要
2. **スケーラビリティ**: 自動スケーリング
3. **コスト効率**: 無料利用枠の活用
4. **AWS統合**: 他サービスとの連携
5. **高可用性**: Multi-AZ自動レプリケーション

### 設計原則
1. **シンプル設計**: 複雑なリレーションは避ける
2. **パフォーマンス重視**: 効率的なキー設計
3. **コスト最適化**: 読み書きキャパシティの最適化
4. **拡張性**: 将来の機能追加を考慮

---

##  テーブル設計

### 1. Users テーブル

#### 基本情報
- **テーブル名**: `portfolio-users`
- **課金モード**: オンデマンド
- **削除保護**: 無効（開発用）
- **暗号化**: SSE (Server-Side Encryption)

#### キー設計
| キータイプ | 属性名 | データ型 | 説明 |
|------------|--------|----------|------|
| Partition Key | `user_id` | String | ユーザーID（プライマリキー） |

#### 属性設計
| 属性名 | データ型 | 必須 | 説明 | 例 |
|--------|----------|------|------|-----|
| `user_id` | String | ✓ | ユーザーID（UUID） | "user_12345678-abcd-1234-efgh-123456789012" |
| `username` | String | ✓ | ユーザー名（ユニーク） | "john_doe" |
| `email` | String | ✓ | メールアドレス | "john@example.com" |
| `created_at` | String | ✓ | 作成日時（ISO8601） | "2025-08-23T10:00:00Z" |
| `updated_at` | String | ✓ | 更新日時（ISO8601） | "2025-08-23T10:00:00Z" |
| `status` | String |  | ユーザーステータス | "active" |

#### インデックス設計
| インデックス名 | タイプ | キー | 用途 |
|----------------|--------|------|------|
| `username-index` | GSI | username (PK) | ユーザー名での検索 |
| `email-index` | GSI | email (PK) | メールアドレスでの検索 |

#### サンプルデータ
```json
{
  "user_id": "user_12345678-abcd-1234-efgh-123456789012",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-08-23T10:00:00Z",
  "updated_at": "2025-08-23T10:00:00Z",
  "status": "active"
}
```

### 2. Metrics テーブル

#### 基本情報
- **テーブル名**: `portfolio-metrics`
- **課金モード**: オンデマンド
- **削除保護**: 無効（開発用）
- **暗号化**: SSE (Server-Side Encryption)

#### キー設計
| キータイプ | 属性名 | データ型 | 説明 |
|------------|--------|----------|------|
| Partition Key | `device_id` | String | デバイスID |
| Sort Key | `timestamp` | Number | タイムスタンプ（UnixTime） |

#### 属性設計
| 属性名 | データ型 | 必須 | 説明 | 例 |
|--------|----------|------|------|-----|
| `device_id` | String | ✓ | デバイスID | "iot_device_001" |
| `timestamp` | Number | ✓ | タイムスタンプ（UnixTime） | 1692782400 |
| `temperature` | Number | ✓ | 温度（摂氏） | 25.5 |
| `humidity` | Number | ✓ | 湿度（%） | 60.2 |
| `status` | String | ✓ | デバイスステータス | "active" |
| `location` | String |  | 設置場所 | "living_room" |
| `battery_level` | Number |  | バッテリー残量（%） | 85 |

#### インデックス設計
| インデックス名 | タイプ | キー | 用途 |
|----------------|--------|------|------|
| `timestamp-index` | GSI | timestamp (PK), device_id (SK) | 時系列での全デバイス検索 |
| `status-index` | GSI | status (PK), timestamp (SK) | ステータス別検索 |

#### サンプルデータ
```json
{
  "device_id": "iot_device_001",
  "timestamp": 1692782400,
  "temperature": 25.5,
  "humidity": 60.2,
  "status": "active",
  "location": "living_room",
  "battery_level": 85
}
```

---

##  アクセスパターン分析

### Users テーブルのアクセスパターン

#### 1. ユーザーID による取得
```
Primary Key: user_id = "user_xxx"
用途: ユーザー詳細情報取得
頻度: 高
```

#### 2. ユーザー名による検索
```
GSI: username-index
用途: ログイン、重複チェック
頻度: 中
```

#### 3. メールアドレスによる検索
```
GSI: email-index 
用途: パスワードリセット、重複チェック
頻度: 低
```

#### 4. 全ユーザー一覧取得
```
Scan操作（ページネーション付き）
用途: 管理画面での一覧表示
頻度: 低
```

### Metrics テーブルのアクセスパターン

#### 1. 特定デバイスの最新データ取得
```
Primary Key: device_id = "iot_device_001"
Sort Key: timestamp (降順)
Limit: 1
用途: ダッシュボード表示
頻度: 高
```

#### 2. 特定デバイスの履歴データ取得
```
Primary Key: device_id = "iot_device_001"
Sort Key: timestamp BETWEEN start_time AND end_time
用途: 時系列グラフ表示
頻度: 中
```

#### 3. 全デバイスの最新データ取得
```
GSI: timestamp-index
Sort Key: timestamp (降順)
FilterExpression: 各device_idの最新のみ
用途: 監視ダッシュボード
頻度: 中
```

#### 4. アラート対象データ取得
```
GSI: status-index
Primary Key: status = "error"
用途: アラート通知
頻度: 低
```

---

##  DynamoDB設定

### テーブル設定

#### Users テーブル
```json
{
  "TableName": "portfolio-users",
  "BillingMode": "PAY_PER_REQUEST",
  "KeySchema": [
    {
      "AttributeName": "user_id",
      "KeyType": "HASH"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "user_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "username", 
      "AttributeType": "S"
    },
    {
      "AttributeName": "email",
      "AttributeType": "S"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "username-index",
      "KeySchema": [
        {
          "AttributeName": "username",
          "KeyType": "HASH"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    },
    {
      "IndexName": "email-index", 
      "KeySchema": [
        {
          "AttributeName": "email",
          "KeyType": "HASH"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    }
  ],
  "SSESpecification": {
    "Enabled": true
  }
}
```

#### Metrics テーブル
```json
{
  "TableName": "portfolio-metrics",
  "BillingMode": "PAY_PER_REQUEST",
  "KeySchema": [
    {
      "AttributeName": "device_id",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "timestamp", 
      "KeyType": "RANGE"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "device_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "timestamp",
      "AttributeType": "N"
    },
    {
      "AttributeName": "status",
      "AttributeType": "S"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "timestamp-index",
      "KeySchema": [
        {
          "AttributeName": "timestamp",
          "KeyType": "HASH"
        },
        {
          "AttributeName": "device_id",
          "KeyType": "RANGE"
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    },
    {
      "IndexName": "status-index",
      "KeySchema": [
        {
          "AttributeName": "status", 
          "KeyType": "HASH"
        },
        {
          "AttributeName": "timestamp",
          "KeyType": "RANGE"  
        }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    }
  ],
  "SSESpecification": {
    "Enabled": true
  }
}
```

---

##  コスト最適化

### 課金設計
- **オンデマンド課金**: 予測困難な負荷に対応
- **無料利用枠**: 25GB/月まで無料
- **リザーブドキャパシティ**: 本番環境では検討

### データ最適化
1. **TTL設定**: 古いメトリクスデータの自動削除
2. **圧縮**: 可能な限り属性名を短縮
3. **インデックス最適化**: 必要最小限のGSI

### TTL設定例（Metricsテーブル）
```json
{
  "AttributeName": "ttl",
  "Enabled": true
}
```
- 90日後に自動削除
- `ttl`属性に削除日時のUnixTimeを設定

---

##  セキュリティ設計

### 暗号化
- **保存時暗号化**: SSE-S3（デフォルト）
- **転送時暗号化**: HTTPS/TLS

### アクセス制御
- **IAMロール**: アプリケーション専用ロール
- **最小権限**: 必要最小限の操作のみ許可

### IAMポリシー例
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem", 
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-users",
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-users/index/*",
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-metrics", 
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-metrics/index/*"
      ]
    }
  ]
}
```

---

##  パフォーマンス最適化

### パーティション設計
- **Users**: `user_id`で均等分散
- **Metrics**: `device_id`で分散、時系列データは`timestamp`でソート

### クエリ最適化
1. **GetItem**: 単一アイテム取得で最高性能
2. **Query**: 効率的な範囲検索
3. **Scan**: 最小限に抑制
4. **BatchGetItem**: 複数アイテム一括取得

### キャッシュ戦略
- **DAX**: DynamoDB Accelerator（将来検討）
- **アプリケーションレベル**: Redis/Memcached（将来検討）

---

##  データ移行・バックアップ

### バックアップ設定
- **Point-in-time Recovery**: 有効化
- **オンデマンドバックアップ**: 重要なタイミングで作成

### データ移行
- **初期データ**: CSVファイルからの一括投入
- **boto3**: Pythonスクリプトでのデータ操作

---

##  運用・メンテナンス

### 監視項目
- **読み書きキャパシティ**: 使用量の監視
- **エラー率**: 4xx/5xxエラーの監視
- **レスポンス時間**: GetItem/Query性能監視

### CloudWatchメトリクス
- `ConsumedReadCapacityUnits`
- `ConsumedWriteCapacityUnits`
- `SuccessfulRequestLatency`
- `ThrottledRequests`

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**次回更新予定**: Phase 3アプリケーション開発時のテーブル作成完了後
