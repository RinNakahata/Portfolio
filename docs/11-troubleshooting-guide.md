#  トラブルシューティングガイド - AWS Portfolio Infrastructure

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **適用環境**: AWS Portfolio Project
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

##  概要

本ドキュメントは、AWS Portfolio Infrastructureの運用において発生する可能性のある問題とその解決方法を体系的に整理したものです。

**対象環境**: 本番環境（AWS）
**更新頻度**: 随時更新
**対象者**: インフラ担当者、開発者

---

##  **緊急時対応手順**

### **サービス停止時の対応フロー**

#### **Step 1: 状況確認（5分以内）**
1. **影響範囲の特定**
   - どのサービスが影響を受けているか
   - 影響を受けるユーザー数
   - ビジネスへの影響度

2. **初期診断**
   - CloudWatchダッシュボードの確認
   - アラートの状況確認
   - ログの確認

#### **Step 2: 緊急対応（15分以内）**
1. **関係者への連絡**
   - ステークホルダーへの状況報告
   - 対応チームの招集
   - ステータスページの更新

2. **一時的な回避策**
   - ロードバランサーの設定変更
   - セキュリティグループの調整
   - リソースの再起動

#### **Step 3: 根本原因の特定（30分以内）**
1. **詳細調査**
   - ログの詳細分析
   - メトリクスの異常値確認
   - 設定変更履歴の確認

2. **原因の特定**
   - 設定ミス
   - リソース不足
   - 外部要因

#### **Step 4: 復旧作業（1時間以内）**
1. **復旧手順の実行**
   - 設定の修正
   - リソースの再作成
   - サービスの再起動

2. **動作確認**
   - ヘルスチェックの確認
   - エンドポイントの動作確認
   - パフォーマンスの確認

---

##  **よくある問題と解決方法**

### **1. ECS/Fargate関連**

#### **問題: タスクが起動しない**
**症状**: ECSサービスでタスクが起動せず、desired countとrunning countが一致しない

**原因と解決方法**:
1. **リソース不足**
   - 解決: タスク定義のCPU/メモリを削減
   - 確認: CloudWatchメトリクスでリソース使用量を確認

2. **IAM権限不足**
   - 解決: ECSタスク実行ロールの権限を確認・修正
   - 確認: CloudTrailログで権限エラーを確認

3. **セキュリティグループ設定**
   - 解決: セキュリティグループのルールを確認・修正
   - 確認: VPC Flow Logsでネットワーク接続を確認

**確認コマンド**:
```bash
# タスクの詳細確認
aws ecs describe-tasks --cluster portfolio-cluster --tasks [task-id]

# タスク定義の確認
aws ecs describe-task-definition --task-definition portfolio-api

# CloudWatchログの確認
aws logs describe-log-streams --log-group-name /aws/ecs/portfolio-api
```

#### **問題: タスクが頻繁に再起動する**
**症状**: タスクが起動後すぐに停止し、再起動を繰り返す

**原因と解決方法**:
1. **ヘルスチェック失敗**
   - 解決: ヘルスチェックエンドポイントの動作確認
   - 確認: アプリケーションログでエラーを確認

2. **メモリ不足**
   - 解決: タスク定義のメモリを増加
   - 確認: CloudWatchメトリクスでメモリ使用量を確認

3. **アプリケーションエラー**
   - 解決: アプリケーションコードの修正
   - 確認: ログでエラーの詳細を確認

**確認コマンド**:
```bash
# タスクの状態確認
aws ecs describe-services --cluster portfolio-cluster --services portfolio-api-service

# ヘルスチェックの確認
curl -f http://[task-ip]:8000/health

# CloudWatchログの確認
aws logs filter-log-events --log-group-name /aws/ecs/portfolio-api --filter-pattern "ERROR"
```

### **2. Application Load Balancer関連**

#### **問題: ターゲットが不健全**
**症状**: ALBのターゲットグループでターゲットがunhealthy状態

**原因と解決方法**:
1. **ヘルスチェックパスが間違っている**
   - 解決: ヘルスチェックパスを正しいパスに修正
   - 確認: `/health`エンドポイントの動作確認

2. **ポート番号が間違っている**
   - 解決: ターゲットグループのポート設定を確認・修正
   - 確認: アプリケーションのリスニングポートを確認

3. **セキュリティグループでポートが閉じている**
   - 解決: セキュリティグループで8000番ポートを開放
   - 確認: セキュリティグループのルールを確認

**確認コマンド**:
```bash
# ターゲットグループの詳細確認
aws elbv2 describe-target-groups --target-group-arns [target-group-arn]

# ターゲットの健全性確認
aws elbv2 describe-target-health --target-group-arn [target-group-arn]

# セキュリティグループの確認
aws ec2 describe-security-groups --group-ids [security-group-id]
```

#### **問題: レスポンス時間が遅い**
**症状**: ALB経由でのレスポンス時間が100msを超える

**原因と解決方法**:
1. **ECSタスクのリソース不足**
   - 解決: タスク定義のCPU/メモリを増加
   - 確認: CloudWatchメトリクスでリソース使用量を確認

2. **DynamoDBの応答遅延**
   - 解決: DynamoDBのキャパシティ設定を確認・調整
   - 確認: DynamoDBメトリクスでレイテンシーを確認

3. **ネットワークの輻輳**
   - 解決: VPC設定の確認・最適化
   - 確認: VPC Flow Logsでネットワーク状況を確認

**確認コマンド**:
```bash
# ALBメトリクスの確認
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB --metric-name TargetResponseTime

# ECSメトリクスの確認
aws cloudwatch get-metric-statistics --namespace AWS/ECS --metric-name CPUUtilization

# DynamoDBメトリクスの確認
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ReadLatency
```

### **3. DynamoDB関連**

#### **問題: スロットリングが発生**
**症状**: DynamoDBでProvisionedThroughputExceededExceptionエラーが発生

**原因と解決方法**:
1. **読み取り/書き込み容量不足**
   - 解決: プロビジョニングされたキャパシティを増加
   - 確認: CloudWatchメトリクスでキャパシティ使用量を確認

2. **ホットキーの問題**
   - 解決: パーティションキーの分散化
   - 確認: アクセスパターンの分析

3. **バーストトラフィック**
   - 解決: オンデマンドモードへの切り替え
   - 確認: トラフィックパターンの分析

**確認コマンド**:
```bash
# テーブルの詳細確認
aws dynamodb describe-table --table-name portfolio-users

# メトリクスの確認
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ConsumedReadCapacityUnits

# スロットリングの確認
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ThrottledRequests
```

#### **問題: テーブルが削除できない**
**症状**: DynamoDBテーブルの削除が失敗する

**原因と解決方法**:
1. **テーブルが使用中**
   - 解決: テーブルを使用しているサービスを停止
   - 確認: CloudTrailログでアクセス状況を確認

2. **バックアップが有効**
   - 解決: バックアップを無効化してから削除
   - 確認: バックアップ設定の確認

3. **グローバルセカンダリインデックスが作成中**
   - 解決: インデックスの作成完了を待つ
   - 確認: テーブルのステータスを確認

**確認コマンド**:
```bash
# テーブルのステータス確認
aws dynamodb describe-table --table-name portfolio-users

# バックアップの確認
aws dynamodb list-backups --table-name portfolio-users

# インデックスの確認
aws dynamodb describe-table --table-name portfolio-users --query 'Table.GlobalSecondaryIndexes'
```

### **4. S3 + CloudFront関連**

#### **問題: CloudFrontでコンテンツが配信されない**
**症状**: CloudFront経由でS3のコンテンツにアクセスできない

**原因と解決方法**:
1. **S3バケットポリシーの問題**
   - 解決: S3バケットポリシーでCloudFrontからのアクセスを許可
   - 確認: バケットポリシーの設定を確認

2. **CloudFrontディストリビューションの設定**
   - 解決: オリジン設定の確認・修正
   - 確認: ディストリビューションの設定を確認

3. **キャッシュの有効期限**
   - 解決: キャッシュ設定の調整
   - 確認: キャッシュ動作の確認

**確認コマンド**:
```bash
# S3バケットポリシーの確認
aws s3api get-bucket-policy --bucket portfolio-static-website-xxxxxxxx

# CloudFrontディストリビューションの確認
aws cloudfront get-distribution --id [distribution-id]

# キャッシュの確認
aws cloudfront get-invalidation --id [invalidation-id] --distribution-id [distribution-id]
```

---

##  **エラーコード対応表**

### **ECS関連エラー**

| エラーコード | エラーメッセージ | 原因 | 解決方法 |
|-------------|------------------|------|----------|
| `CLIENT_ERROR` | Task failed to start | タスク定義の問題 | タスク定義の確認・修正 |
| `RESOURCE_REQUIRED` | Insufficient CPU units | CPU不足 | タスク定義のCPU増加 |
| `RESOURCE_REQUIRED` | Insufficient memory | メモリ不足 | タスク定義のメモリ増加 |
| `MISSING_ATTRIBUTE` | Task role not found | IAMロール不足 | タスクロールの作成・設定 |

### **ALB関連エラー**

| エラーコード | エラーメッセージ | 原因 | 解決方法 |
|-------------|------------------|------|----------|
| `502 Bad Gateway` | Target not responding | ターゲットが応答しない | ターゲットの健全性確認 |
| `503 Service Unavailable` | No healthy targets | 健全なターゲットなし | ターゲットの状態確認 |
| `504 Gateway Timeout` | Target timeout | ターゲットの応答遅延 | タイムアウト設定の調整 |

### **DynamoDB関連エラー**

| エラーコード | エラーメッセージ | 原因 | 解決方法 |
|-------------|------------------|------|----------|
| `ProvisionedThroughputExceededException` | Rate exceeded | キャパシティ不足 | キャパシティの増加 |
| `ResourceNotFoundException` | Table not found | テーブルが存在しない | テーブル名の確認 |
| `ValidationException` | Invalid parameter | パラメータが無効 | パラメータの確認・修正 |

---

##  **復旧手順**

### **ECSサービスの復旧**

#### **手順1: サービス状態の確認**
```bash
# サービスの状態確認
aws ecs describe-services --cluster portfolio-cluster --services portfolio-api-service

# タスクの状態確認
aws ecs list-tasks --cluster portfolio-cluster --service-name portfolio-api-service
```

#### **手順2: サービスの更新**
```bash
# サービスの強制更新
aws ecs update-service --cluster portfolio-cluster --service portfolio-api-service --force-new-deployment

# タスク数の調整
aws ecs update-service --cluster portfolio-cluster --service portfolio-api-service --desired-count 2
```

#### **手順3: 動作確認**
```bash
# ヘルスチェックの確認
curl -f http://[alb-dns-name]/health

# ログの確認
aws logs filter-log-events --log-group-name /aws/ecs/portfolio-api --filter-pattern "ERROR"
```

### **DynamoDBテーブルの復旧**

#### **手順1: テーブル状態の確認**
```bash
# テーブルの状態確認
aws dynamodb describe-table --table-name portfolio-users

# メトリクスの確認
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ConsumedReadCapacityUnits
```

#### **手順2: キャパシティの調整**
```bash
# 読み取りキャパシティの増加
aws dynamodb update-table --table-name portfolio-users --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5

# オンデマンドモードへの切り替え
aws dynamodb update-table --table-name portfolio-users --billing-mode PAY_PER_REQUEST
```

#### **手順3: 動作確認**
```bash
# テーブルの動作確認
aws dynamodb scan --table-name portfolio-users --limit 1

# メトリクスの確認
aws cloudwatch get-metric-statistics --namespace AWS/DynamoDB --metric-name ThrottledRequests
```

### **ALBの復旧**

#### **手順1: ターゲットグループの確認**
```bash
# ターゲットグループの状態確認
aws elbv2 describe-target-groups --target-group-arns [target-group-arn]

# ターゲットの健全性確認
aws elbv2 describe-target-health --target-group-arn [target-group-arn]
```

#### **手順2: ターゲットの登録**
```bash
# ターゲットの登録
aws elbv2 register-targets --target-group-arn [target-group-arn] --targets Id=[target-id],Port=8000

# ターゲットの登録解除
aws elbv2 deregister-targets --target-group-arn [target-group-arn] --targets Id=[target-id]
```

#### **手順3: 動作確認**
```bash
# ヘルスチェックの確認
curl -f http://[alb-dns-name]/health

# ターゲットの健全性確認
aws elbv2 describe-target-health --target-group-arn [target-group-arn]
```

---

##  **ログ分析のポイント**

### **CloudWatch Logsの分析**

#### **エラーログの検索**
```bash
# エラーログの検索
aws logs filter-log-events --log-group-name /aws/ecs/portfolio-api --filter-pattern "ERROR"

# 特定の時間範囲でのログ検索
aws logs filter-log-events --log-group-name /aws/ecs/portfolio-api --start-time [timestamp] --end-time [timestamp]

# 特定のパターンのログ検索
aws logs filter-log-events --log-group-name /aws/ecs/portfolio-api --filter-pattern "Exception"
```

#### **ログの分析ポイント**
1. **エラーメッセージ**: エラーの詳細な内容
2. **タイムスタンプ**: エラーが発生した時刻
3. **コンテキスト**: エラーが発生した状況
4. **スタックトレース**: エラーの発生箇所

### **CloudTrailログの分析**

#### **API呼び出しの追跡**
```bash
# 特定のユーザーのAPI呼び出し
aws logs filter-log-events --log-group-name [cloudtrail-log-group] --filter-pattern "userName"

# 特定のリソースへのアクセス
aws logs filter-log-events --log-group-name [cloudtrail-log-group] --filter-pattern "resourceName"
```

#### **分析のポイント**
1. **アクセスパターン**: 異常なアクセスパターンの検出
2. **権限変更**: IAM権限の変更履歴
3. **リソース作成・削除**: リソースの変更履歴
4. **エラー**: API呼び出しの失敗履歴

---

##  **予防的メンテナンス**

### **定期チェック項目**

#### **日次チェック**
- [ ] CloudWatchアラートの確認
- [ ] サービス状態の確認
- [ ] ログの異常確認
- [ ] コスト使用量の確認

#### **週次チェック**
- [ ] パフォーマンスメトリクスの確認
- [ ] セキュリティ設定の確認
- [ ] バックアップの確認
- [ ] 容量使用量の確認

#### **月次チェック**
- [ ] セキュリティ監査の実施
- [ ] パフォーマンス分析の実施
- [ ] コスト最適化の検討
- [ ] ドキュメントの更新

### **監視設定の最適化**

#### **アラートの設定**
1. **高重要度アラート**
   - サービス停止
   - セキュリティインシデント
   - コスト超過

2. **中重要度アラート**
   - パフォーマンス低下
   - リソース使用量増加
   - エラー率増加

3. **低重要度アラート**
   - 情報提供
   - 定期メンテナンス
   - 設定変更

---

##  **関連ドキュメント**

- `docs/08-operations-checklist.md` - 運用項目一覧
- `docs/09-management-ledger.md` - 管理台帳
- `docs/10-operations-report.md` - 運用報告書

---

