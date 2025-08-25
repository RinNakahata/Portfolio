  # Rin Nakahata Portfolio



  ##  ご挨拶
  ご覧いただきありがとうございます。
  本ポートフォリオは、AWS環境におけるインフラ構築スキルをご確認いただくために作成しました。

  ##  ポートフォリオ概要

  **モダンなクラウドネイティブアプリケーション**を想定。
  以下の機能を提供する、実用的なWebアプリケーション・API基盤として設計しました。

  ###  機能概要

  #### **RESTful API機能**
  - **ユーザー管理**: ユーザー登録、認証、プロフィール管理
  - **メトリクス管理**: IoTデバイスやシステムメトリクスの収集・分析
  - **リアルタイム監視**: システム状態のリアルタイム監視とアラート
  - **ヘルスチェック**: アプリケーションとデータベース接続の健全性確認

  #### **Webインターフェース**
  - **管理ダッシュボード**: システム状態とメトリクスの可視化
  - **API テストツール**: ブラウザから直接APIをテスト可能
  - **リアルタイム更新**: 監視データのライブ更新表示
  - **レスポンシブデザイン**: モバイル・デスクトップ対応

  #### **インフラストラクチャ機能**
  - **自動スケーリング**: トラフィックに応じた自動スケールアウト/イン
  - **高可用性**: 複数AZでの冗長構成
  - **CDN配信**: CloudFrontによる高速コンテンツ配信
  - **ロードバランシング**: ALBによる負荷分散
  - **セキュアな通信**: HTTPS/TLS暗号化

  ###  技術的な特徴
  - **Infrastructure as Code**: Terraformによる完全自動化
  - **コンテナ化**: Dockerによる環境の標準化
  - **CI/CD**: GitHub Actionsによる自動デプロイ
  - **監視・ログ**: CloudWatch統合監視
  - **コスト最適化**: サーバーレス・オンデマンド課金設計



  ##  システム構成
```
  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
  │   CloudFront    │────│       ALB        │────│   ECS/Fargate   │
  │   (Static Web)  │    │  (Load Balancer) │    │ (Python API)    │
  └─────────────────┘    └──────────────────┘    └─────────────────┘
           │                        │                        │
           ▼                        │                        ▼
  ┌─────────────────┐               │              ┌─────────────────┐
  │       S3        │               │              │    DynamoDB     │
  │  (Static Files) │               │              │   (Database)    │
  └─────────────────┘               │              └─────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │   CloudWatch    │
                          │  (Monitoring)   │
                          └─────────────────┘
```


  ### 主要コンポーネント
  - **フロントエンド**: S3 + CloudFront (静的サイトホスティング)
  - **バックエンドAPI**: Python (Flask/FastAPI) on ECS/Fargate
  - **データベース**: DynamoDB
  - **インフラ管理**: Terraform (Infrastructure as Code)
  - **コンテナ化**: Docker
  - **監視**: CloudWatch + CloudWatch Logs



  ##  プロジェクト構造
```
  ├── terraform/          # Terraformインフラコード
  ├── src/                # Pythonアプリケーションソース
  ├── docker/            # Docker関連設定
  ├── docs/              # 設計ドキュメント
  ├── scripts/           # デプロイ・運用スクリプト
  └── .github/workflows/ # CI/CD設定
```



  ##  開発環境

  - **メイン開発**: WSL2 Ubuntu 22.04
  - **ドキュメント作成**: GitHub Web Editor
  - **インフラ管理**: Terraform
  - **コンテナ**: Docker & Docker Compose



  ##  技術スタック

  ### インフラストラクチャ
  - AWS (ECS, ALB, DynamoDB, S3, CloudFront, CloudWatch)
  - Terraform
  - Docker

  ### アプリケーション
  - Python 3.x
  - Flask/FastAPI
  - boto3 (AWS SDK)

  ### 開発・運用
  - Git & GitHub
  - GitHub Actions (CI/CD)
  - AWS CLI



  ##  ドキュメント

  ###  設計・仕様書
  - 詳細な設計書やAPI仕様書は [`docs/`](docs/) ディレクトリに格納されています

  ###  開発・運用ドキュメント
  - [`TODO.md`](TODO.md) - 詳細な作業計画・進捗管理
  - [`.env.example`](.env.example) - 環境設定ファイルテンプレート

  ###  Docker関連
  - [`Dockerfile`](Dockerfile) - 本番用コンテナ設定
  - [`Dockerfile.dev`](Dockerfile.dev) - 開発用コンテナ設定
  - [`docker-compose.yml`](docker-compose.yml) - 本番環境構成
  - [`docker-compose.dev.yml`](docker-compose.dev.yml) - 開発環境構成

  ##  クイックスタート

  ### ローカル開発環境での作業開始

  ### 前提条件
  - AWS CLI設定済み
  - Terraform インストール済み
  - Docker インストール済み
  - Python 3.11以上

  ### ローカル開発環境起動
  ```bash
  # リポジトリクローン
  git clone https://github.com/RinNakahata/portfolio-aws-infrastructure.git
  cd portfolio-aws-infrastructure

  # 環境設定
  cp .env.example .env
  # .env ファイルを編集してAWS認証情報を設定

  # 開発環境起動（DynamoDB Local付き）
  docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

  # API動作確認
  curl http://localhost:8000/api/v1/health
  ```

  ### AWS環境構築
  ```bash
  # Terraformでインフラ構築
  cd terraform
  terraform init
  terraform plan
  terraform apply

  # CI/CDでの自動デプロイ
  git push origin main  # GitHub Actionsで自動デプロイ
  ```


##  開発ステータス

**現在の開発進捗**: **Phase 0 完了 - 設計・基盤構築完了**

###  Phase 0 完了内容（2025-08-25）
- ✅ **Terraformインフラコード**: 完全検証済み（VPC、ECS/Fargate、DynamoDB、S3、CloudFront）
- ✅ **Python API設計**: FastAPI + DynamoDB完全アーキテクチャ
- ✅ **Docker環境**: 本番・開発用コンテナ化完了
- ✅ **CI/CD**: GitHub Actions設定済み
- ✅ **開発準備**: 実装作業のための完全な準備完了

###  次回作業予定（Phase 1-4）
1. **環境セットアップ** - 開発環境の最終確認・準備
2. **アプリケーション実装** - API実装、DynamoDB連携、テスト作成
3. **AWS環境構築** - 実際のクラウド環境デプロイ・動作確認
4. **最終調整** - 監視設定、ドキュメント完成、ポートフォリオ公開

詳細な開発計画は `TODO.md` を参照してください。

##  ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

##  作成者

中畑 倫 _ Rin Nakahata
