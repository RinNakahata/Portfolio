# docker-compose ガイド

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **対象**: 複数コンテナ管理を学びたい人
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

---

##  学習目標

この資料を読むことで以下ができるようになります：
1. docker-composeの基本概念を理解する
2. docker-compose.ymlファイルを記述できる
3. 複数サービスの連携を管理できる
4. 開発環境での活用方法を理解する

---

##  docker-composeとは？

### 問題：複数コンテナの管理の複雑さ
```bash
# 手動でのマルチコンテナ起動
docker network create app-network
docker run -d --name database --network app-network postgres:13
docker run -d --name redis --network app-network redis:alpine  
docker run -d --name api --network app-network -p 8000:8000 myapi:latest
docker run -d --name frontend --network app-network -p 3000:3000 myfrontend:latest
```

### 解決：docker-composeによる統合管理
```yaml
# docker-compose.yml
version: '3.8'
services:
  database:
    image: postgres:13
  redis:
    image: redis:alpine
  api:
    image: myapi:latest
    ports:
      - "8000:8000"
  frontend:
    image: myfrontend:latest
    ports:
      - "3000:3000"
```

```bash
# 1コマンドで全サービス起動
docker-compose up
```

### docker-composeの定義
**docker-compose**: 複数のDockerコンテナを定義・実行するためのツール

---

##  基本構成

### docker-compose.ymlの基本構造
```yaml
version: '3.8'  # Compose file format version

services:       # サービス（コンテナ）定義
  service1:
    # サービス1の設定
  service2:
    # サービス2の設定

volumes:        # 永続化ボリューム定義（オプション）
  volume1:
    
networks:       # ネットワーク定義（オプション）
  network1:
```

### 最小構成の例
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
  
  app:
    image: python:3.11-slim
    command: python -m http.server 8000
    ports:
      - "8000:8000"
```

---

##  基本的なサービス設定

### 1. image - イメージ指定
```yaml
services:
  web:
    # Docker Hubのイメージ
    image: nginx:1.21-alpine
  
  app:
    # ローカルビルドイメージ
    image: myapp:latest
```

### 2. build - ローカルビルド
```yaml
services:
  app:
    # Dockerfileからビルド
    build: .
    
  api:
    # ビルドオプション指定
    build:
      context: ./api
      dockerfile: Dockerfile.dev
      args:
        - ENVIRONMENT=development
```

### 3. ports - ポート公開
```yaml
services:
  web:
    ports:
      # ホスト:コンテナ
      - "8080:80"
      - "8443:443"
      # IPアドレス指定
      - "127.0.0.1:8000:8000"
```

### 4. environment - 環境変数
```yaml
services:
  app:
    environment:
      # key: value 形式
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      
  api:
    # オブジェクト形式
    environment:
      NODE_ENV: development
      DEBUG: "true"
```

### 5. volumes - データ永続化
```yaml
services:
  database:
    image: postgres:13
    volumes:
      # 名前付きボリューム
      - postgres_data:/var/lib/postgresql/data
      # ホストディレクトリマウント  
      - ./config:/app/config
      # 匿名ボリューム
      - /app/logs

volumes:
  postgres_data:
```

### 6. depends_on - 依存関係
```yaml
services:
  web:
    depends_on:
      - database
      - redis
    
  database:
    image: postgres:13
    
  redis:
    image: redis:alpine
```

### 7. networks - ネットワーク
```yaml
services:
  frontend:
    networks:
      - frontend-network
      
  backend:
    networks:
      - frontend-network
      - backend-network
      
  database:
    networks:
      - backend-network

networks:
  frontend-network:
  backend-network:
    internal: true  # 外部アクセス禁止
```

---

##  実践例

### 1. Web アプリケーション (Frontend + Backend + DB)

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # フロントエンド
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - app-network

  # バックエンドAPI
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@database:5432/portfolio
      - ENVIRONMENT=development
    depends_on:
      - database
      - redis
    volumes:
      - ./backend:/app
      - backend_logs:/app/logs
    networks:
      - app-network

  # データベース
  database:
    image: postgres:13-alpine
    environment:
      POSTGRES_DB: portfolio
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network

  # Redis（キャッシュ）
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  backend_logs:

networks:
  app-network:
    driver: bridge
```

### 2. 開発環境用設定

#### docker-compose.dev.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    volumes:
      # ホットリロード用
      - ./backend:/app
      - /app/node_modules
    command: nodemon app.js

  frontend:
    build:
      context: ./frontend  
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # 開発用ツール
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    depends_on:
      - database
```

#### 使用方法
```bash
# 開発環境起動
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# または
docker-compose --profile dev up
```

---

## 🎛 基本コマンド

### 1. サービス管理
```bash
# 全サービス起動（バックグラウンド）
docker-compose up -d

# 特定サービスのみ起動
docker-compose up frontend backend

# サービス停止
docker-compose down

# サービス停止 + ボリューム削除
docker-compose down -v

# サービス再起動
docker-compose restart

# 特定サービス再起動
docker-compose restart backend
```

### 2. ビルド・更新
```bash
# イメージビルド
docker-compose build

# キャッシュなしビルド
docker-compose build --no-cache

# ビルドしてから起動
docker-compose up --build

# サービス更新（新しいイメージ取得）
docker-compose pull
```

### 3. ログ・デバッグ
```bash
# 全サービスのログ表示
docker-compose logs

# 特定サービスのログ
docker-compose logs backend

# リアルタイムログ
docker-compose logs -f

# ログ行数制限
docker-compose logs --tail=100 backend
```

### 4. サービス操作
```bash
# サービス一覧表示
docker-compose ps

# サービス内でコマンド実行
docker-compose exec backend bash
docker-compose exec database psql -U postgres

# 一回限りのコマンド実行
docker-compose run --rm backend python manage.py migrate
```

### 5. スケーリング
```bash
# サービス複製
docker-compose up --scale backend=3

# 複数サービススケール
docker-compose up --scale backend=3 --scale worker=2
```

---

##  高度な設定

### 1. 環境変数ファイル
```yaml
# docker-compose.yml
services:
  backend:
    env_file:
      - .env
      - .env.local
```

#### .env
```
DATABASE_URL=postgresql://postgres:password@database:5432/portfolio
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key
```

### 2. プロファイル
```yaml
services:
  app:
    # 常に起動
    image: myapp:latest
    
  database:
    # 常に起動
    image: postgres:13
    
  debug-tools:
    # devプロファイルでのみ起動
    image: adminer
    profiles: ["dev"]
```

```bash
# プロファイル指定起動
docker-compose --profile dev up
```

### 3. ヘルスチェック
```yaml
services:
  backend:
    image: myapi:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

### 4. リソース制限
```yaml
services:
  backend:
    image: myapi:latest
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

---

##  ベストプラクティス

### 1. ファイル分割
```bash
# ベース設定
docker-compose.yml

# 開発環境用オーバーライド
docker-compose.dev.yml

# 本番環境用オーバーライド  
docker-compose.prod.yml

# テスト環境用
docker-compose.test.yml
```

### 2. 環境変数管理
```yaml
#  ハードコードは避ける
environment:
  DATABASE_PASSWORD: secret123

#  環境変数で管理
environment:
  DATABASE_PASSWORD: ${DATABASE_PASSWORD}
```

### 3. ボリューム管理
```yaml
volumes:
  # 名前付きボリューム（推奨）
  postgres_data:
    driver: local
    
  # ホストパス指定（開発時のみ）
  - ./app:/app  # ホットリロード用
```

### 4. ネットワーク分離
```yaml
networks:
  # 外部向けネットワーク
  frontend:
    
  # 内部専用ネットワーク
  backend:
    internal: true
```

---

##  本プロジェクト用構成

### ローカル開発用 docker-compose.yml
```yaml
version: '3.8'

services:
  # Portfolio API
  api:
    build: 
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - AWS_REGION=ap-northeast-1
      - DYNAMODB_ENDPOINT=http://dynamodb-local:8000
    depends_on:
      - dynamodb-local
    volumes:
      - .:/app
      - /app/.venv  # 仮想環境除外
    networks:
      - portfolio-network

  # ローカル DynamoDB
  dynamodb-local:
    image: amazon/dynamodb-local:latest
    command: -jar DynamoDBLocal.jar -sharedDb -dbPath ./data
    ports:
      - "8001:8000"
    volumes:
      - dynamodb_data:/home/dynamodblocal/data
    networks:
      - portfolio-network

  # DynamoDB Admin UI
  dynamodb-admin:
    image: aaronshaf/dynamodb-admin:latest
    environment:
      - DYNAMO_ENDPOINT=http://dynamodb-local:8000
    ports:
      - "8002:8001"
    depends_on:
      - dynamodb-local
    networks:
      - portfolio-network

  # Static Web Server (開発用)
  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
    networks:
      - portfolio-network

volumes:
  dynamodb_data:

networks:
  portfolio-network:
    driver: bridge
```

### 起動・管理コマンド
```bash
# 開発環境起動
docker-compose up -d

# APIのみ起動
docker-compose up -d api dynamodb-local

# ログ確認
docker-compose logs -f api

# API コンテナ内でコマンド実行
docker-compose exec api bash
docker-compose exec api python -m pytest

# 停止・クリーンアップ
docker-compose down -v
```

---

##  トラブルシューティング

### 1. ポート競合
```bash
# エラー: port is already allocated
# 解決: 使用中ポートの確認・変更
docker-compose ps
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### 2. ボリュームの権限問題
```yaml
# 解決: ユーザーID指定
services:
  app:
    user: "${UID}:${GID}"
    volumes:
      - .:/app
```

### 3. ネットワーク接続問題
```bash
# ネットワーク確認
docker network ls
docker network inspect <network_name>

# コンテナ間の接続テスト
docker-compose exec service1 ping service2
```

---

##  チェックリスト

### 開発環境セットアップ
- [ ] docker-compose.yml作成
- [ ] .env ファイル設定
- [ ] .dockerignore 作成
- [ ] ポート設定確認
- [ ] ボリュームマウント設定

### 運用準備
- [ ] プロダクション用設定分離
- [ ] 環境変数管理
- [ ] ヘルスチェック設定
- [ ] リソース制限設定
- [ ] ログ管理設定

---

##  参考リソース

### 公式ドキュメント
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose file reference](https://docs.docker.com/compose/compose-file/)

### 実用例
- [Awesome Docker Compose Examples](https://github.com/docker/awesome-compose)

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**次回学習**: Dockerベストプラクティス
