#  Rin Nakahata's Portfolio

初めまして。中畑 倫 (Rin Nakahata)と申します。
ご覧いただきありがとうございます。

##  プロジェクト概要

このプロジェクトは、AWS環境構築スキルを証明するための包括的なポートフォリオです。**IaC化、コンテナ化、CI/CD、モニタリング**など、実務で求められるスキルを網羅的に実装しています。

##  主要機能

###  インフラストラクチャ
- **VPC設計**: マルチAZ構成のセキュアなネットワーク
- **ECS/Fargate**: サーバーレスコンテナオーケストレーション
- **ALB**: 高可用性ロードバランサー
- **DynamoDB**: フルマネージドNoSQLデータベース
- **S3 + CloudFront**: 静的コンテンツ配信
- **ECR**: コンテナイメージレジストリ
- **CloudWatch**: 包括的なモニタリング・ログ管理

###  バックエンドAPI
- **FastAPI**: 高速なPython Webフレームワーク
- **Pydantic**: データバリデーション・シリアライゼーション
- **DynamoDB統合**: 完全なCRUD操作
- **構造化ログ**: 運用性を重視したログ出力
- **包括的エラーハンドリング**: カスタム例外クラスとハンドラー

###  フロントエンド
- **レスポンシブデザイン**: モダンなUI/UX
- **リアルタイム更新**: メトリクスデータの動的表示
- **ダッシュボード**: 直感的なデータ可視化

###  CI/CD
- **GitHub Actions**: 自動化されたデプロイメント
- **Terraform**: インフラの自動プロビジョニング
- **マルチ環境対応**: 開発・ステージング・本番環境

##  システムアーキテクチャ

**静的コンテンツフロー (上部):**
```
User Request → CloudFront (CDN) → S3 (Static Files)
```

**動的APIフロー (下部):**
```
User Request → ALB/ELB → ECS/Fargate → DynamoDB → CloudWatch
```

**詳細なアーキテクチャ図:**
```
+--------------+     +--------------+     +--------------+
|    User      | --> |  CloudFront  | --> |      S3      |
|   Request    |     |    (CDN)     |     |(Static Files)|
+--------------+     +--------------+     +--------------+
        |
        v
+--------------+     +--------------+     +--------------+     +--------------+
|   ALB/ELB    | --> | ECS/Fargate  | --> |   DynamoDB   | --> |  CloudWatch  |
| Load Balancer|     | Python API   |     |  (Database)  |     | (Monitoring) |
+--------------+     +--------------+     +--------------+     +--------------+

```

**フロー説明:**

1. **静的コンテンツフロー**:
   - ユーザーリクエスト → CloudFront CDN → S3静的ファイル
   - フロントエンド・HTML/CSS/JS・画像ファイルの配信

2. **動的APIフロー**:
   - ユーザーリクエスト → ALB負荷分散 → ECS/Fargateコンテナ → DynamoDBデータベース → CloudWatch監視
   - バックエンドAPI・データ処理・システム監視

##  プロジェクト構造

```
Portfolio/
├── 📁 docs/                          # 設計・運用ドキュメント
│   ├── 01-architecture.md            # システムアーキテクチャ
│   ├── 02-system-requirements.md     # システム要件定義
│   ├── 03-technology-selection.md    # 技術選定書
│   ├── 04-api-specification.md       # API仕様書
│   ├── 05-database-design.md         # データベース設計書
│   ├── 06-infrastructure-design.md   # インフラ設計書
│   ├── 07-security-design.md         # セキュリティ設計書
│   ├── 08-operations-checklist.md    # 運用項目一覧
│   ├── 09-management-ledger.md       # 管理台帳
│   ├── 10-operations-report.md       # 運用報告書
│   └── 11-troubleshooting-guide.md   # トラブルシューティングガイド
├── 📁 src/                           # アプリケーションソース
│   ├── 📁 app/                       # メインアプリケーション
│   │   ├── 📁 core/                  # コア機能
│   │   │   ├── config.py             # 設定管理
│   │   │   ├── logging.py            # ログ設定
│   │   │   ├── exceptions.py         # カスタム例外クラス
│   │   │   └── error_handlers.py     # エラーハンドラー
│   │   ├── 📁 models/                # データモデル
│   │   │   ├── user.py               # ユーザーモデル
│   │   │   └── metric.py             # メトリクスモデル
│   │   ├── 📁 routers/               # APIルーター
│   │   │   ├── health.py             # ヘルスチェック
│   │   │   ├── users.py              # ユーザー管理
│   │   │   └── metrics.py            # メトリクス管理
│   │   ├── 📁 services/              # ビジネスロジック
│   │   │   ├── user_service.py       # ユーザーサービス
│   │   │   └── metric_service.py     # メトリクスサービス
│   │   └── dependencies.py           # 依存関係管理
│   ├── 📁 frontend/                  # フロントエンド
│   │   ├── index.html                # メインページ
│   │   ├── style.css                 # スタイルシート
│   │   └── script.js                 # JavaScript
│   ├── main.py                       # アプリケーションエントリーポイント
│   └── requirements.txt              # Python依存関係
├── 📁 tests/                         # テストコード
│   ├── conftest.py                   # pytest設定・フィクスチャ
│   ├── test_user_service.py          # ユーザーサービステスト
│   ├── test_metric_service.py        # メトリクスサービステスト
│   └── test_api_integration.py       # API統合テスト
├── 📁 terraform/                     # インフラストラクチャ・アズ・コード
│   ├── main.tf                       # メイン設定
│   ├── variables.tf                  # 変数定義
│   ├── outputs.tf                    # 出力定義
│   └── versions.tf                   # プロバイダーバージョン
├── 📁 .github/                       # GitHub Actions
│   └── 📁 workflows/
│       └── deploy.yml                # CI/CDパイプライン
├── 📁 docker/                        # Docker設定
├── docker-compose.yml                # ローカル開発環境
├── pytest.ini                        # pytest設定
└── README.md                         # プロジェクト概要
```

##  技術スタック

### **インフラストラクチャ**
- **AWS**: VPC, ECS/Fargate, ALB, DynamoDB, S3, CloudFront, ECR, CloudWatch, IAM
- **Terraform**: AWS Provider 5.0, インフラの自動化
- **Docker**: コンテナ化、マルチステージビルド

### **バックエンド**
- **Python 3.11**: 高速で保守性の高い言語
- **FastAPI**: 非同期対応、自動APIドキュメント生成
- **Pydantic**: データバリデーション、型安全性
- **Boto3**: AWS SDK for Python

### **フロントエンド**
- **HTML5/CSS3**: セマンティックマークアップ、レスポンシブデザイン
- **JavaScript (ES6+)**: モダンなJavaScript機能
- **Chart.js**: データ可視化ライブラリ

### **開発・運用**
- **GitHub Actions**: CI/CDパイプライン
- **pytest**: 包括的なテストフレームワーク
- **Black/Flake8**: コード品質管理
- **構造化ログ**: 運用性を重視したログ出力

##  開発環境セットアップ

### **前提条件**
- Python 3.11+
- Docker & Docker Compose
- AWS CLI (本番環境用)
- Terraform (本番環境用)

### **ローカル環境起動**
```bash
# リポジトリクローン
git clone https://github.com/RinNakahata/Portfolio.git
cd Portfolio

# 依存関係インストール
pip install -r src/requirements.txt

# Docker環境起動
docker-compose up -d

# アプリケーション起動
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **テスト実行**
```bash
# 全テスト実行
pytest

# 特定のテスト実行
pytest tests/test_user_service.py -v

# カバレッジ付きテスト実行
pytest --cov=src --cov-report=html
```

##  現在の開発進捗

**現在の開発進捗**: **Phase 0-1 完了 - 設計・基盤・実装・テスト構築完了**

### **Phase 0 完了内容**
- [x] **システム設計**: 7つの設計書が完成
- [x] **インフラ設計**: Terraformコード完成
- [x] **Python API設計**: FastAPI + DynamoDB完全アーキテクチャ
- [x] **フロントエンド**: レスポンシブUI完成
- [x] **CI/CD設定**: GitHub Actions完成
- [x] **運用ドキュメント**: 11件の包括的なドキュメント完成

### **Phase 1 完了内容**
- [x] **サービス層実装**: UserService・MetricServiceの完全実装
- [x] **エラーハンドリング**: カスタム例外クラス・ハンドラー完成
- [x] **構造化ログ**: 運用性を重視したログシステム完成
- [x] **テストコード**: 包括的なテストスイート完成
- [x] **設定管理**: 環境別設定ファイル完成

### **次回作業予定（Phase 2-4）**
1. **ローカル環境動作確認** - Docker環境でのAPI動作確認
2. **AWS環境構築** - 実際のクラウド環境デプロイ・動作確認
3. **最終調整** - 監視設定、スクリーンショット・動画記録、ポートフォリオ公開

##  次のステップ

**設計・実装・テストは完了**

次のフェーズでは以下の作業を行います：

1. **ローカル環境の動作確認**
   - Docker環境起動
   - APIエンドポイントの動作確認
   - DynamoDB Localとの連携確認

2. **AWS環境へのデプロイ**
   - `terraform apply`の実行
   - ECS/Fargateでの動作確認
   - CloudWatch監視の確認

3. **ポートフォリオ完成**
   - スクリーンショット・動画記録
   - 最終動作確認
   - 環境クリーンアップ

##  コスト最適化

- **AWS Free Tier**: 12ヶ月間の無料利用
- **ECS Fargate**: 使用時のみ課金
- **DynamoDB**: 25GBまで無料
- **S3**: 5GBまで無料
- **CloudFront**: 1TBまで無料

**月額予算**: $10以下を目標

##  貢献方法

1. このリポジトリをフォーク
2. フィーチャーブランチを作成
3. 変更をコミット
4. プルリクエストを作成

##  ライセンス

このプロジェクトはMITライセンスの下で公開されています。

##  作者

**Rin Nakahata** 

---
