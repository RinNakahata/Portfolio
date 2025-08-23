# API仕様書

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **API Version**: v1
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

---

##  API概要

### 目的
- DynamoDBとの連携によるデータ操作
- RESTful APIの実装例を示す
- ポートフォリオ用のサンプルアプリケーション

### ベースURL
```
Production:  https://api.portfolio-aws.com/v1
Development: https://dev-api.portfolio-aws.com/v1
Local:       http://localhost:8000/v1
```

### プロトコル
- **HTTPS**: 本番環境
- **HTTP**: 開発・ローカル環境

---

##  エンドポイント一覧

### ヘルスチェック
| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/health` | アプリケーション稼働状況 |
| GET | `/health/db` | データベース接続確認 |

### ユーザー管理
| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/users` | ユーザー一覧取得 |
| POST | `/users` | ユーザー新規作成 |
| GET | `/users/{user_id}` | ユーザー詳細取得 |
| PUT | `/users/{user_id}` | ユーザー情報更新 |
| DELETE | `/users/{user_id}` | ユーザー削除 |

### IoTメトリクス管理
| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/metrics` | メトリクス一覧取得 |
| POST | `/metrics` | メトリクス新規登録 |
| GET | `/metrics/{device_id}` | デバイス別メトリクス取得 |
| GET | `/metrics/latest` | 最新メトリクス取得 |

---

##  エンドポイント詳細仕様

### 1. ヘルスチェック

#### GET /health
アプリケーションの稼働状況を確認

**レスポンス:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T10:00:00Z",
  "version": "1.0.0",
  "service": "portfolio-api"
}
```

#### GET /health/db
データベース接続状況を確認

**レスポンス:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-08-23T10:00:00Z",
  "response_time_ms": 25
}
```

### 2. ユーザー管理API

#### GET /users
ユーザー一覧を取得

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 | デフォルト |
|------------|----|----- |------|------------|
| limit | integer | 任意 | 取得件数 | 20 |
| offset | integer | 任意 | オフセット | 0 |
| sort | string | 任意 | ソート順 (created_at, username) | created_at |
| order | string | 任意 | 昇順/降順 (asc, desc) | desc |

**レスポンス:**
```json
{
  "users": [
    {
      "user_id": "user_001",
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2025-08-23T09:00:00Z",
      "updated_at": "2025-08-23T09:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### POST /users
新規ユーザーを作成

**リクエストボディ:**
```json
{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**バリデーション:**
- `username`: 必須、3-50文字、英数字とアンダースコアのみ
- `email`: 必須、有効なメールアドレス形式

**レスポンス (201 Created):**
```json
{
  "user_id": "user_001",
  "username": "john_doe", 
  "email": "john@example.com",
  "created_at": "2025-08-23T10:00:00Z",
  "updated_at": "2025-08-23T10:00:00Z"
}
```

#### GET /users/{user_id}
特定ユーザーの詳細情報を取得

**パスパラメータ:**
- `user_id`: ユーザーID（必須）

**レスポンス (200 OK):**
```json
{
  "user_id": "user_001",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-08-23T09:00:00Z",
  "updated_at": "2025-08-23T09:00:00Z"
}
```

**レスポンス (404 Not Found):**
```json
{
  "error": "User not found",
  "error_code": "USER_NOT_FOUND",
  "message": "User with ID 'user_001' not found"
}
```

#### PUT /users/{user_id}
ユーザー情報を更新

**リクエストボディ:**
```json
{
  "username": "john_doe_updated",
  "email": "john.new@example.com"
}
```

**レスポンス (200 OK):**
```json
{
  "user_id": "user_001",
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "created_at": "2025-08-23T09:00:00Z",
  "updated_at": "2025-08-23T10:30:00Z"
}
```

#### DELETE /users/{user_id}
ユーザーを削除

**レスポンス (204 No Content):**
```
(レスポンスボディなし)
```

### 3. IoTメトリクス管理API

#### GET /metrics
IoTメトリクスの一覧を取得

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|------------|----|----- |------|
| device_id | string | 任意 | デバイスID |
| start_time | integer | 任意 | 開始時刻（UnixTime） |
| end_time | integer | 任意 | 終了時刻（UnixTime） |
| limit | integer | 任意 | 取得件数（デフォルト: 100） |

**レスポンス:**
```json
{
  "metrics": [
    {
      "device_id": "iot_device_001",
      "timestamp": 1692782400,
      "temperature": 25.5,
      "humidity": 60.2,
      "status": "active"
    }
  ],
  "total": 1,
  "limit": 100
}
```

#### POST /metrics
新しいメトリクスを登録

**リクエストボディ:**
```json
{
  "device_id": "iot_device_001",
  "temperature": 25.5,
  "humidity": 60.2,
  "status": "active"
}
```

**バリデーション:**
- `device_id`: 必須、文字列
- `temperature`: 必須、-50.0 ～ 100.0
- `humidity`: 必須、0.0 ～ 100.0  
- `status`: 必須、["active", "inactive", "error"]

**レスポンス (201 Created):**
```json
{
  "device_id": "iot_device_001",
  "timestamp": 1692782400,
  "temperature": 25.5,
  "humidity": 60.2,
  "status": "active"
}
```

#### GET /metrics/{device_id}
特定デバイスのメトリクス履歴を取得

**クエリパラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|------------|----|----- |------|
| start_time | integer | 任意 | 開始時刻（UnixTime） |
| end_time | integer | 任意 | 終了時刻（UnixTime） |
| limit | integer | 任意 | 取得件数 |

**レスポンス:**
```json
{
  "device_id": "iot_device_001",
  "metrics": [
    {
      "timestamp": 1692782400,
      "temperature": 25.5,
      "humidity": 60.2,
      "status": "active"
    }
  ],
  "total": 1
}
```

#### GET /metrics/latest
全デバイスの最新メトリクスを取得

**レスポンス:**
```json
{
  "latest_metrics": [
    {
      "device_id": "iot_device_001",
      "timestamp": 1692782400,
      "temperature": 25.5,
      "humidity": 60.2,
      "status": "active"
    }
  ],
  "total_devices": 1,
  "last_updated": "2025-08-23T10:00:00Z"
}
```

---

##  エラーレスポンス

### 共通エラーフォーマット
```json
{
  "error": "エラーメッセージ",
  "error_code": "ERROR_CODE",
  "message": "詳細なエラーメッセージ",
  "timestamp": "2025-08-23T10:00:00Z"
}
```

### HTTPステータスコード

| コード | 説明 | 例 |
|--------|------|-----|
| 200 | 成功 | データ取得成功 |
| 201 | 作成成功 | ユーザー作成成功 |
| 204 | 削除成功 | ユーザー削除成功 |
| 400 | リクエストエラー | バリデーションエラー |
| 404 | リソース未存在 | ユーザーが見つからない |
| 500 | サーバーエラー | データベース接続エラー |

### エラーコード一覧

| エラーコード | HTTPコード | 説明 |
|--------------|------------|------|
| `VALIDATION_ERROR` | 400 | バリデーションエラー |
| `USER_NOT_FOUND` | 404 | ユーザーが見つからない |
| `DEVICE_NOT_FOUND` | 404 | デバイスが見つからない |
| `DUPLICATE_USERNAME` | 400 | ユーザー名が重複 |
| `DUPLICATE_EMAIL` | 400 | メールアドレスが重複 |
| `DATABASE_ERROR` | 500 | データベースエラー |
| `INTERNAL_ERROR` | 500 | 内部サーバーエラー |

---

##  レート制限

### 制限内容
- **一般API**: 100 requests/minute/IP
- **メトリクス投稿**: 1000 requests/minute/IP
- **ヘルスチェック**: 制限なし

### レート制限ヘッダー
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1692782460
```

---

##  認証（将来拡張）

現在のバージョンでは認証機能は実装しませんが、将来的には以下を検討：

- **API Key認証**: `X-API-Key` ヘッダー
- **JWT Token**: Bearer Token認証
- **AWS Cognito**: AWSマネージド認証サービス

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**次回更新予定**: Phase 3アプリケーション開発開始時
