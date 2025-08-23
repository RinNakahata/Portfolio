##  プロジェクト進捗

**現在のフェーズ**: Phase 0 - 環境構築（Week 1）  
**開始日**: 2025-08-23

---

##  完了済み

### Phase 0: Day 1 - プロジェクト初期設定
- [x] GitHubで新規リポジトリを作成する
- [x] プロジェクトのディレクトリ構造を作成する
- [x] README.mdを作成する  
- [x] .gitignoreを作成する（Python）
- [x] TODO.mdを作成する
- [x] LICENSEファイルを追加する（MIT）

---

##  予定タスク

### Phase 0: Day 1 - 設計ドキュメント作成

- [ ] docs/architecture.mdの骨子を作成する
- [ ] draw.ioでAWS構成図の下書きを作成する
- [ ] システム要件を文書化する
- [ ] 技術選定理由を文書化する

### Phase 0: Day 2-3 - 環境構築

#### WSL2/Ubuntu環境
- [ ] WSL2を有効化する
- [ ] Ubuntu 22.04をインストールする
- [ ] Ubuntuの初期設定を完了する
- [ ] aptパッケージを最新化する
- [ ] 基本開発ツールをインストールする
- [ ] Python3と pip をインストールする
- [ ] VSCodeをインストールする
- [ ] VSCodeのWSL拡張機能をインストールする

#### Docker環境
- [ ] Docker公式GPGキーを追加する
- [ ] Dockerリポジトリを追加する
- [ ] Docker CEをインストールする
- [ ] 現在のユーザーをdockerグループに追加する
- [ ] Dockerサービスの起動を確認する
- [ ] `docker run hello-world`で動作確認する

#### 開発ツール設定
- [ ] AWS CLIをインストールする
- [ ] Terraformをインストールする
- [ ] Git設定（ユーザー名、メール）を行う
- [ ] SSH鍵を生成する
- [ ] SSH公開鍵をGitHubに登録する
- [ ] リポジトリをローカルにクローンする

### Phase 0: Day 4-5 - 設計と計画

#### 詳細設計書作成
- [ ] API仕様の詳細設計を作成する
- [ ] データベース設計を作成する
- [ ] インフラ構成の詳細設計を作成する
- [ ] セキュリティ設計を作成する

#### AWS構成図作成
- [ ] draw.ioで全体構成図を完成させる
- [ ] ネットワーク構成図を作成する
- [ ] データフロー図を作成する
- [ ] 構成図をGitHubにアップロードする

### Phase 0: Day 6-7 - Docker基礎学習

#### Docker学習資料作成
- [ ] Docker基礎概念をまとめる
- [ ] Dockerfile記述方法をまとめる
- [ ] docker-compose概要をまとめる
- [ ] ベストプラクティスをまとめる

#### Docker実践
- [ ] 簡単なPython Flaskアプリを作成する
- [ ] Dockerfileを作成する
- [ ] Dockerイメージをビルドする
- [ ] コンテナを起動してテストする
- [ ] docker-compose.ymlを作成する
- [ ] 複数コンテナの連携を確認する

---

##  Phase 1-5 (今後の予定)

### Phase 1: AWS基盤構築（Week 2）
- AWS初期設定、IAM設定
- Terraform基本ファイル作成・実装
- VPC、セキュリティグループ構築

### Phase 2: ECS/Fargate実装（Week 3-4）
- ECS設計・実装
- ALB構築
- Docker Image & ECR連携

### Phase 3: アプリケーション開発（Week 5）
- Python API実装
- DynamoDB連携
- フロントエンド作成

### Phase 4: 運用設計（Week 6）
- CloudWatch監視設定
- アラート設定
- ダッシュボード構築

### Phase 5: ドキュメント作成（Week 7-8）
- 技術ドキュメント完成
- ポートフォリオ公開準備
- 環境クリーンアップ

---


##  完了基準

- [ ] GitHubリポジトリが公開されている
- [ ] Terraformコードが完成している
- [ ] Dockerイメージがビルドできる
- [ ] ドキュメントがGitHub Pagesで閲覧できる
- [ ] 構築手順書通りに環境構築できる
- [ ] AWS環境のスクリーンショットがある
- [ ] 実装した機能の説明が明確である

---

**最終更新**: 2025-08-23  
**次回更新予定**: Phase 0 Day 1 完了後
