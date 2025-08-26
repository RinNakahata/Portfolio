# 自宅PC用作業リスト - Phase 2: ローカル環境動作確認

**現在の状況**: Phase 2進行中 - AWS環境設定完了（設計・基盤・実装・テスト・AWS環境構築完了）
**次回再開時の作業**: Phase 2継続 - ローカル環境動作確認

**次回はこのコマンドで即座にPhase 2を継続できます**:
```bash
docker-compose up -d
curl http://localhost:8000/api/v1/health
```

---

## 📋 作業概要

現在、会社PCで設計・実装・テスト環境の構築が100%完了しています。
自宅PCでは「Phase 2: ローカル環境動作確認」を実行し、実際にアプリケーションを動かして動作確認を行います。

---

## 🏠 Phase 2: ローカル環境動作確認

### 0️⃣ 環境設定ファイルの準備 **<完了>**

#### .envファイルの作成 **<完了>**
```bash
# ✅ 完了済み - AWS環境情報設定済み
# ECR: 731219764430.dkr.ecr.ap-northeast-1.amazonaws.com/portfolio-api
# ECS Cluster: portfolio-cluster-001
# DynamoDB: portfolio-users, portfolio-metrics
# CloudFront: d18zbgswhqb84s.cloudfront.net
# AWSアクセスキー: 設定済み
```

### 1️⃣ 基本環境構築

#### 前提条件の確認
```bash
# Python 3.11+のインストール確認
python --version

# Dockerの動作確認  
docker --version
docker-compose --version

# Gitの動作確認
git --version
```

#### 依存関係のインストール
```bash
# Python仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows

# 依存関係のインストール
pip install -r src/requirements.txt
```

### 2️⃣ Docker環境起動

#### DynamoDB Local + API環境の起動
```bash
# Docker環境の起動（バックグラウンド実行）
docker-compose up -d

# ログの確認
docker-compose logs -f api
```

#### サービスの動作確認
```bash
# API Health Check
curl http://localhost:8000/api/v1/health

# DynamoDB Admin UI（ブラウザで確認）
# http://localhost:8002
```

**📸 スクリーンショット撮影ポイント**
- [ ] Docker Desktopでコンテナが起動している画面
- [ ] ターミナルでdocker-compose upの成功ログ
- [ ] http://localhost:8002 のDynamoDB Admin UI画面

### 3️⃣ FastAPIアプリケーション起動

#### 開発サーバーの起動
```bash
# srcディレクトリに移動して起動
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### API動作確認
```bash
# APIドキュメントの確認（ブラウザ）
# http://localhost:8000/docs

# 基本的なエンドポイントテスト
curl -X GET http://localhost:8000/api/v1/health
curl -X GET http://localhost:8000/api/v1/users
curl -X GET http://localhost:8000/api/v1/metrics
```

**📸 スクリーンショット撮影ポイント**
- [ ] FastAPI Swagger UI (http://localhost:8000/docs) の画面
- [ ] API Health Checkの成功レスポンス画面
- [ ] ターミナルでのAPI起動ログ

### 4️⃣ DynamoDB連携確認

#### DynamoDBテーブルの確認
```bash
# DynamoDB Admin UIでテーブル確認
# http://localhost:8002

# テーブル一覧の確認
aws dynamodb list-tables --endpoint-url http://localhost:8001
```

#### CRUD操作テスト
```bash
# ユーザー作成テスト
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"テストユーザー","email":"test@example.com"}'

# メトリクス作成テスト  
curl -X POST http://localhost:8000/api/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{"name":"test_metric","value":100}'
```

**📸 スクリーンショット撮影ポイント**
- [ ] DynamoDB Admin UIでテーブル一覧画面
- [ ] 作成したユーザーデータがDynamoDB Admin UIで表示される画面
- [ ] 作成したメトリクスデータがDynamoDB Admin UIで表示される画面
- [ ] curl でPOSTリクエストの成功レスポンス画面

### 5️⃣ フロントエンド動作確認

#### 静的ファイルの確認
```bash
# フロントエンドファイルの確認
# src/frontend/index.html をブラウザで開く

# または、簡易HTTPサーバーで確認
cd src/frontend
python -m http.server 8080
# http://localhost:8080 でアクセス
```

**📸 スクリーンショット撮影ポイント**
- [ ] フロントエンドのメイン画面 (http://localhost:8080)
- [ ] フロントエンドがAPIからデータを取得している画面
- [ ] レスポンシブデザインの確認（スマホサイズでの表示）

### 6️⃣ テスト実行・品質確認

#### 全テストの実行
```bash
# 全テスト実行
pytest

# 詳細なカバレッジレポート生成
pytest --cov=src --cov-report=html

# HTML カバレッジレポートの確認
# htmlcov/index.html をブラウザで開く
```

**📸 スクリーンショット撮影ポイント**
- [ ] pytestの実行結果（全テストPASS）画面
- [ ] カバレッジレポート（>90%）の画面
- [ ] HTMLカバレッジレポートのサマリー画面

#### コード品質チェック
```bash
# コードフォーマット確認
black --check src/ tests/

# インポート順序確認
isort --check src/ tests/

# リント実行
flake8 src/ tests/

# 型チェック
mypy src/
```

**📸 スクリーンショット撮影ポイント**
- [ ] 全コード品質チェックがPASSしている画面

### 7️⃣ エラーハンドリング・ログ確認

#### エラーハンドリングテスト
```bash
# 存在しないエンドポイント
curl http://localhost:8000/api/v1/nonexistent

# 不正なデータ
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

#### ログ出力の確認
```bash
# Dockerログの確認
docker-compose logs api

# アプリケーションログの確認（構造化ログ）
tail -f logs/app.log  # ログファイルが生成される場合
```

**📸 スクリーンショット撮影ポイント**
- [ ] エラーハンドリングが正常動作している画面
- [ ] 構造化ログが適切に出力されている画面

---

## 🎯 Phase 2完了の判定基準

### ✅ 完了チェックリスト

**機能確認**
- [ ] .envファイルが正常に作成・設定済み
- [ ] Python仮想環境が正常に作成・アクティベート済み
- [ ] 全依存関係が正常にインストール済み
- [ ] Docker環境（API + DynamoDB Local）が正常起動
- [ ] FastAPIアプリケーションが正常起動
- [ ] APIのHealth Checkが正常レスポンス
- [ ] DynamoDB Localとの接続確認済み
- [ ] 基本的なCRUD操作が正常動作
- [ ] フロントエンドが正常表示
- [ ] 全テストがPASS（カバレッジ >90%）
- [ ] コード品質チェックがすべてPASS
- [ ] エラーハンドリングが正常動作
- [ ] ログが適切に出力される

**ポートフォリオ用記録**
- [ ] Docker Desktop起動画面のスクリーンショット
- [ ] DynamoDB Admin UI画面のスクリーンショット
- [ ] FastAPI Swagger UI画面のスクリーンショット
- [ ] CRUD操作成功画面のスクリーンショット  
- [ ] フロントエンド表示画面のスクリーンショット
- [ ] テスト実行結果画面のスクリーンショット
- [ ] カバレッジレポート画面のスクリーンショット
- [ ] 全体動作の動画撮影（3-5分程度）

### 📊 期待する結果

1. **API**: `http://localhost:8000/docs` でSwagger UIが表示される
2. **Database**: DynamoDB Admin UI でテーブルとデータが確認できる
3. **Frontend**: フロントエンドが正常に表示され、APIと連携する
4. **Tests**: すべてのテストが成功し、高いカバレッジを維持
5. **Logs**: 構造化ログが適切に出力される

---

## 🚨 トラブルシューティング

### よくある問題と解決策

#### Docker関連
```bash
# ポート競合の場合
docker-compose down
netstat -tulpn | grep :8000  # ポート使用状況確認

# Dockerボリュームのクリア
docker-compose down -v
docker system prune -a
```

#### Python環境関連
```bash
# 依存関係の問題
pip install --upgrade pip
pip install -r src/requirements.txt --force-reinstall
```

#### API接続問題
- Firewall設定の確認
- localhost vs 127.0.0.1 の使い分け
- ポート番号の確認（8000, 8001, 8002）

---

## ⏭️ Phase 3への準備

Phase 2が完了したら、次は「Phase 3: AWS環境構築・デプロイ」に進みます。

### Phase 3で必要なもの
- AWSアカウント（Free Tier）
- AWS CLI設定
- Terraformコマンド
- 本番用設定ファイル

### Phase 3でやること
1. AWS認証情報設定
2. Terraformでインフラ構築
3. ECS/Fargateにデプロイ
4. CloudWatch監視設定

---

## 📝 重要な注意点

1. **作業環境**: 自宅PCでリラックスして作業
2. **時間管理**: Phase 2は2日間目安
3. **品質重視**: すべてのテストがPASSすることを確認
4. **ドキュメント**: 問題があれば `docs/11-troubleshooting-guide.md` 参照
5. **バックアップ**: 作業前にgitでコミット推奨

**頑張って！ 🚀**