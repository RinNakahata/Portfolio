  # Rin Nakahata Portfolio

  ##  リポジトリ概要
  ご覧いただきありがとうございます。  
  本リポジトリは、AWS環境におけるインフラ構築スキルをご確認いただくために作成しました。

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

  ├── terraform/          # Terraformインフラコード
  ├── src/                # Pythonアプリケーションソース
  ├── docker/            # Docker関連設定
  ├── docs/              # 設計ドキュメント
  ├── scripts/           # デプロイ・運用スクリプト
  └── .github/workflows/ # CI/CD設定

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

  詳細な設計書やAPI仕様書は `docs/` ディレクトリに格納されています。

  ##  クイックスタート

  ### 前提条件
  - AWS CLI設定済み
  - Terraform インストール済み
  - Docker インストール済み

  ### デプロイ手順
  ```bash
  # リポジトリクローン
  git clone https://github.com/[username]/portfolio-aws-infrastructure.git
  cd portfolio-aws-infrastructure

  # インフラ構築
  cd terraform
  terraform init
  terraform plan
  terraform apply

  # アプリケーションデプロイ
  cd ../scripts
  ./deploy.sh

   開発ステータス

  現在の開発進捗: Phase 0 - プロジェクト初期設定

  詳細な開発計画は TODO.md を参照してください。

   ライセンス

  MIT License - 詳細は LICENSE ファイルを参照してください。

   作成者

  中畑 倫 _ Rin Nakahata
