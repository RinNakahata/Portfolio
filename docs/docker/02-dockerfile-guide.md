# Dockerfile記述方法 ガイド

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **対象**: チーム内で Dockerfileの習熟度が低いメンバー
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

---

##  学習目標

この資料を読むことで以下ができるようになります：
1. Dockerfileの基本構文を理解する
2. 効率的なDockerfileを記述する  
3. セキュリティを考慮したDockerfileを作成する
4. 本プロジェクトに適用可能なDockerfileを書ける

---

##  Dockerfileとは

### 定義
**Dockerfile**: Dockerイメージを作成するためのテキストファイル形式のレシピ

### 基本的な流れ
```
Dockerfile → docker build → Docker Image → docker run → Container
```

### Dockerfileの例
```dockerfile
# ベースイメージ指定
FROM python:3.11-slim

# 作業ディレクトリ設定  
WORKDIR /app

# ファイルコピー
COPY requirements.txt .

# パッケージインストール
RUN pip install -r requirements.txt

# アプリケーションコード追加
COPY . .

# ポート公開
EXPOSE 8000

# 実行コマンド
CMD ["python", "app.py"]
```

---

##  基本命令

### 1. FROM - ベースイメージ指定
```dockerfile
# 公式イメージを使用
FROM python:3.11-slim

# 特定バージョン指定
FROM node:18.17.0-alpine

# マルチステージビルド用
FROM python:3.11-slim as builder
```

**選択ポイント:**
- **公式イメージ優先**: セキュリティ・安定性
- **タグ指定**: `latest`は避ける
- **軽量版**: `-slim`, `-alpine`を検討

### 2. WORKDIR - 作業ディレクトリ設定
```dockerfile
# 作業ディレクトリ作成・移動
WORKDIR /app

# 複数階層のディレクトリも作成可能
WORKDIR /app/src/main
```

**ベストプラクティス:**
- 絶対パス使用
- `/app`が一般的
- 毎回`cd`する代わりに使用

### 3. COPY vs ADD - ファイル追加
```dockerfile
# COPY: ローカルファイル → コンテナ（推奨）
COPY requirements.txt .
COPY src/ /app/src/

# ADD: より多機能だが複雑
ADD archive.tar.gz /app/  # 自動展開される
ADD https://example.com/file.txt /app/  # URL取得
```

**使い分け:**
- **COPY**: 通常のファイルコピー
- **ADD**: 自動展開・URL取得が必要な場合のみ

### 4. RUN - コマンド実行
```dockerfile
# シェルコマンド実行
RUN apt-get update && apt-get install -y curl

# 複数コマンドを1つのRUNで実行（レイヤー最適化）
RUN apt-get update \
    && apt-get install -y \
       curl \
       wget \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# exec形式（推奨）
RUN ["pip", "install", "-r", "requirements.txt"]
```

### 5. EXPOSE - ポート公開
```dockerfile
# ポート公開宣言（ドキュメント用途）
EXPOSE 8000
EXPOSE 80 443

# 実際の公開は docker run -p で行う
```

### 6. ENV - 環境変数設定
```dockerfile
# 環境変数設定
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 複数まとめて設定
ENV ENVIRONMENT=production \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1
```

### 7. ARG - ビルド引数
```dockerfile
# ビルド時引数定義
ARG PYTHON_VERSION=3.11
ARG APP_VERSION=1.0.0

# 使用例
FROM python:${PYTHON_VERSION}-slim
LABEL version=${APP_VERSION}

# デフォルト値設定
ARG PORT=8000
EXPOSE ${PORT}
```

### 8. LABEL - メタデータ
```dockerfile
# イメージにメタデータ追加
LABEL maintainer="developer@example.com"
LABEL version="1.0.0"
LABEL description="Portfolio API Application"

# 複数ラベルをまとめて
LABEL maintainer="developer@example.com" \
      version="1.0.0" \
      description="Portfolio API Application"
```

### 9. USER - 実行ユーザー指定
```dockerfile
# 非rootユーザー作成・使用（セキュリティ向上）
RUN useradd --create-home --shell /bin/bash app
USER app

# UIDでの指定も可能
USER 1000:1000
```

### 10. CMD vs ENTRYPOINT - 実行コマンド
```dockerfile
# CMD: デフォルトコマンド（上書き可能）
CMD ["python", "app.py"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# ENTRYPOINT: 必ず実行されるコマンド
ENTRYPOINT ["python", "app.py"]

# 組み合わせ使用
ENTRYPOINT ["python", "app.py"]
CMD ["--help"]
```

---

## 🏗 実践例

### 1. Python FastAPI アプリケーション

#### シンプル版
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 最適化版
```dockerfile
# マルチステージビルド
FROM python:3.11-slim as builder

# システムパッケージ更新（セキュリティ）
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 依存関係インストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ランタイムイメージ
FROM python:3.11-slim

# セキュリティ更新
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 非rootユーザー作成
RUN useradd --create-home --shell /bin/bash app

# Python パッケージコピー
COPY --from=builder /root/.local /home/app/.local

# 作業ディレクトリ・権限設定
WORKDIR /app
CHOWN app:app /app

# アプリケーションコード
COPY --chown=app:app . .

# 非rootユーザーに切り替え
USER app

# PATH追加
ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Node.js アプリケーション
```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# package.jsonのみ先にコピー（キャッシュ効率化）
COPY package*.json ./
RUN npm ci --only=production

# プロダクション用イメージ
FROM node:18-alpine

# 非rootユーザー
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app

# 依存関係とアプリケーションコピー
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
```

---

##  最適化テクニック

### 1. レイヤーキャッシュ活用

####  非効率
```dockerfile
# 変更頻度の高いファイルを先にコピー
COPY . .
RUN pip install -r requirements.txt
```

####  効率的
```dockerfile
# 変更頻度の低いファイルを先にコピー
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 2. マルチステージビルド
```dockerfile
# ビルドステージ
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# プロダクションステージ
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

### 3. .dockerignore 活用
```dockerignore
# 不要なファイルを除外
node_modules
.git
.gitignore
README.md
.env
.env.local
*.log
coverage
.pytest_cache
__pycache__
```

### 4. RUN命令最適化
```dockerfile
#  レイヤーが多い
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN apt-get clean

#  1つのレイヤーに統合
RUN apt-get update \
    && apt-get install -y \
       python3 \
       pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

---

##  セキュリティベストプラクティス

### 1. 非rootユーザー使用
```dockerfile
# ユーザー作成・切り替え
RUN useradd --create-home --shell /bin/bash app
USER app
```

### 2. 最新セキュリティパッチ適用
```dockerfile
# システムパッケージ更新
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean
```

### 3. 不要なパッケージ削除
```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && pip install -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean
```

### 4. 機密情報の除外
```dockerfile
#  機密情報を含めない
ENV DATABASE_PASSWORD=secret123

#  ランタイムで設定
ENV DATABASE_PASSWORD=""
```

---

##  本プロジェクト用 Dockerfile

### Portfolio API用 Dockerfile
```dockerfile
FROM python:3.11-slim as builder

# Build dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production image
FROM python:3.11-slim

# Security updates
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --shell /bin/bash --uid 1001 app

# Copy Python packages
COPY --from=builder /root/.local /home/app/.local

# Application code
WORKDIR /app
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Environment variables
ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

##  便利なDockerfileパターン

### 1. 環境別ビルド
```dockerfile
ARG ENVIRONMENT=development

FROM python:3.11-slim

# 環境別設定
COPY requirements.txt .
RUN if [ "$ENVIRONMENT" = "production" ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt; \
    fi
```

### 2. バージョン管理
```dockerfile
ARG VERSION=latest
LABEL version=${VERSION}

# バージョン情報を環境変数に
ENV APP_VERSION=${VERSION}
```

### 3. 動的ポート設定
```dockerfile
ARG PORT=8000
ENV PORT=${PORT}
EXPOSE ${PORT}
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT}
```

---

##  デバッグ・テスト

### 1. ビルド過程の確認
```bash
# ビルド履歴表示
docker history myapp:latest

# 中間レイヤーも表示
docker build --progress=plain -t myapp:latest .
```

### 2. イメージサイズ最適化確認
```bash
# イメージサイズ確認
docker images myapp:latest

# レイヤー詳細確認
docker inspect myapp:latest
```

### 3. セキュリティスキャン
```bash
# 脆弱性スキャン
docker scan myapp:latest
```

---

##  チェックリスト

### ビルド時チェック
- [ ] ベースイメージのタグ指定
- [ ] .dockerignoreファイル作成
- [ ] レイヤー数の最小化
- [ ] キャッシュ効率化
- [ ] 非rootユーザー使用

### セキュリティチェック  
- [ ] 最新セキュリティパッチ適用
- [ ] 不要パッケージ削除
- [ ] 機密情報の除外
- [ ] HEALTHCHECK設定
- [ ] 脆弱性スキャン実施

---

##  参考リソース

### 公式ドキュメント
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/)

### セキュリティガイド
- [Docker Security](https://docs.docker.com/engine/security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**次回学習**: docker-compose概要
