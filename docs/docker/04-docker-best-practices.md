# Docker ベストプラクティス

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **対象**: Docker運用を最適化したい人
- **作成者**: Portfolio Project
- **最終更新**: 2025-08-23

---

##  学習目標

この資料を読むことで以下ができるようになります：
1. プロダクション品質のDockerイメージを作成できる
2. セキュリティを考慮したDocker運用ができる
3. パフォーマンス最適化技術を適用できる
4. 運用・デバッグのベストプラクティスを実践できる

---

##  イメージ作成のベストプラクティス

### 1. ベースイメージ選択

####  推奨
```dockerfile
# 公式イメージ + 具体的なタグ
FROM python:3.11-slim

# Alpine版（軽量）
FROM node:18-alpine

# 特定バージョン指定
FROM postgres:15.4-alpine
```

####  避けるべき
```dockerfile
# latest タグは避ける
FROM python:latest

# 非公式イメージ
FROM someone/python-custom

# メジャーバージョンのみ
FROM python:3
```

**理由:**
- `latest`は予期しない更新でビルドが壊れる可能性
- 公式イメージは定期的にセキュリティ更新される
- 具体的なバージョン指定で再現性を保証

### 2. 軽量イメージ作成

#### マルチステージビルド
```dockerfile
# ビルドステージ
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# 実行ステージ
FROM node:18-alpine AS runtime
WORKDIR /app

# 非rootユーザー作成
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# 必要ファイルのみコピー
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

USER nextjs
CMD ["npm", "start"]
```

#### レイヤー最適化
```dockerfile
#  複数のRUN命令
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get clean

#  1つのRUN命令に統合
RUN apt-get update && \
    apt-get install -y \
        curl \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 3. キャッシュ効率化

#### 変更頻度に基づく順序
```dockerfile
#  変更頻度の低いものを先に
FROM python:3.11-slim

# システムパッケージ（変更頻度: 低）
RUN apt-get update && apt-get install -y curl

# Python依存関係（変更頻度: 中）  
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションコード（変更頻度: 高）
COPY . .
```

#### .dockerignoreの活用
```dockerignore
# バージョン管理
.git
.gitignore

# ログ・一時ファイル
*.log
*.tmp
__pycache__
.pytest_cache

# 開発環境ファイル
.env.local
.vscode
.idea

# ドキュメント
README.md
docs/

# テスト関連
tests/
coverage/

# 依存関係（コンテナ内でインストール）
node_modules
.venv
```

---

##  セキュリティベストプラクティス

### 1. 非rootユーザーの使用

#### Linuxベース
```dockerfile
FROM python:3.11-slim

# 非rootユーザー作成
RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid app --shell /bin/bash --create-home app

# 作業ディレクトリ準備
WORKDIR /app
RUN chown app:app /app

# アプリケーション設定
COPY --chown=app:app . .

# 非rootユーザーに切り替え
USER app

CMD ["python", "app.py"]
```

#### Alpineベース
```dockerfile
FROM python:3.11-alpine

# Alpine用ユーザー作成
RUN addgroup -g 1001 -S app && \
    adduser -u 1001 -S app -G app

WORKDIR /app
COPY --chown=app:app . .

USER app
CMD ["python", "app.py"]
```

### 2. セキュリティ更新の適用

```dockerfile
FROM ubuntu:22.04

# セキュリティ更新
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 3. 機密情報の管理

####  避けるべき
```dockerfile
# 機密情報をDockerfileに直接記載
ENV DATABASE_PASSWORD=secret123
ENV API_KEY=abcd1234

# 機密ファイルをイメージに含める
COPY .env .
```

####  推奨
```dockerfile
# 実行時に環境変数で渡す
ENV DATABASE_PASSWORD=""
ENV API_KEY=""

# Docker Secrets使用（Docker Swarm）
# またはKubernetes Secrets使用
```

```bash
# 実行時に環境変数指定
docker run -e DATABASE_PASSWORD=secret123 myapp:latest

# 環境変数ファイル使用
docker run --env-file .env myapp:latest
```

---

##  パフォーマンス最適化

### 1. イメージサイズ最適化

#### 不要パッケージの削除
```dockerfile
FROM python:3.11-slim

# ビルド用パッケージをインストール・削除
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    pip install psycopg2-binary && \
    apt-get purge -y \
        build-essential \
        libpq-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

#### Python固有の最適化
```dockerfile
# Python バイトコードファイル作成無効化
ENV PYTHONDONTWRITEBYTECODE=1

# stdout/stderrのバッファリング無効化
ENV PYTHONUNBUFFERED=1  

# pipキャッシュ削除
RUN pip install --no-cache-dir -r requirements.txt

# __pycache__ 削除
RUN find /app -type d -name __pycache__ -exec rm -rf {} +
```

### 2. ビルド最適化

#### 依存関係のキャッシュ
```dockerfile
#  依存関係のキャッシュが効かない
COPY . .
RUN pip install -r requirements.txt

#  requirements.txtを先にコピー
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

#### 並列ビルド
```bash
# 複数CPUコアでビルド
docker build --build-arg MAKEFLAGS="-j$(nproc)" -t myapp .
```

### 3. ランタイム最適化

#### ヘルスチェック
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

#### ログ設定
```dockerfile
# 構造化ログの有効化
ENV LOG_FORMAT=json
ENV LOG_LEVEL=info

# アプリケーション内でのログ設定
ENV PYTHONUNBUFFERED=1
```

---

##  開発・デバッグ

### 1. 開発効率化

#### ホットリロード設定
```yaml
# docker-compose.dev.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      # ソースコードマウント
      - .:/app
      # node_modules除外
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev
```

#### デバッグ用Dockerfile
```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

# 開発用パッケージ追加
RUN pip install debugpy ipdb

# デバッグポート公開
EXPOSE 5678

# デバッグモードで起動
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "app.py"]
```

### 2. ログ・監視

#### 構造化ログ
```python
# アプリケーション内でのログ設定例
import logging
import json
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_entry)

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

#### メトリクス収集
```dockerfile
# Prometheusメトリクス用ポート
EXPOSE 9090

# メトリクス収集設定
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir
RUN mkdir -p /tmp/prometheus_multiproc_dir
```

---

##  運用ベストプラクティス

### 1. イメージ管理

#### タグ戦略
```bash
# セマンティックバージョニング
docker build -t myapp:1.2.3 .
docker build -t myapp:1.2 .
docker build -t myapp:1 .

# Git コミットハッシュ
docker build -t myapp:${GITHUB_SHA} .

# ブランチ別
docker build -t myapp:main .
docker build -t myapp:develop .
```

#### イメージクリーンアップ
```bash
# 使用されていないイメージ削除
docker image prune -f

# 古いイメージの自動削除
docker system prune -a --filter "until=24h"
```

### 2. コンテナ管理

#### リソース制限
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### 再起動ポリシー
```yaml
services:
  app:
    restart: unless-stopped
    # always, no, on-failure, unless-stopped
```

### 3. 監視・アラート

#### ヘルスチェック
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

#### ログ管理
```bash
# ログローテーション設定
docker run \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  myapp:latest
```

---

##  本プロジェクト適用例

### プロダクション用 Dockerfile
```dockerfile
# マルチステージビルド
FROM python:3.11-slim AS builder

# ビルド依存関係
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python依存関係インストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 実行ステージ
FROM python:3.11-slim AS runtime

# セキュリティ更新
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        dumb-init && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 非rootユーザー作成
RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid app --shell /bin/bash --create-home app

# Python パッケージ
COPY --from=builder /root/.local /home/app/.local

# アプリケーション
WORKDIR /app
COPY --chown=app:app . .

# 非rootユーザーに切り替え
USER app

# 環境変数
ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# メタデータ
LABEL maintainer="portfolio@example.com" \
      version="1.0.0" \
      description="Portfolio API Application"

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# dumb-initでPID 1問題解決
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### CI/CD統合
```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Cache Docker layers
        uses: actions/cache@v3
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-buildx-
            
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            myregistry/portfolio-api:latest
            myregistry/portfolio-api:${{ github.sha }}
          cache-from: type=local,src=/tmp/.buildx-cache
          cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

---

##  チェックリスト

### イメージ作成時
- [ ] 公式ベースイメージ使用
- [ ] 具体的なタグ指定
- [ ] .dockerignore作成
- [ ] マルチステージビルド採用
- [ ] レイヤー最適化
- [ ] セキュリティ更新適用
- [ ] 非rootユーザー使用

### セキュリティ
- [ ] 機密情報の除外
- [ ] 最小権限の原則
- [ ] ベースイメージの脆弱性チェック
- [ ] 定期的なセキュリティ更新

### パフォーマンス
- [ ] イメージサイズ最適化
- [ ] キャッシュ効率化
- [ ] ヘルスチェック設定
- [ ] リソース制限設定

### 運用
- [ ] 適切なタグ戦略
- [ ] ログ設定
- [ ] 監視設定
- [ ] バックアップ戦略

---

##  参考リソース

### 公式ガイド
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### セキュリティ
- [Docker Security Best Practices](https://docs.docker.com/engine/security/security/)
- [NIST Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)

### パフォーマンス
- [Docker Performance Optimization](https://docs.docker.com/config/containers/resource_constraints/)

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**プロジェクト適用**: これらのベストプラクティスを本プロジェクトのDocker実装に適用し、プロダクション品質のインフラを構築しましょう。
