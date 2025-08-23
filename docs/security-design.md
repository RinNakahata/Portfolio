# セキュリティ設計書

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **適用環境**: AWS Portfolio Project
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

---

##  セキュリティ設計方針

### 基本原則
1. **最小権限の原則**: 必要最小限のアクセス権限のみ付与
2. **深層防御**: 複数のセキュリティレイヤーによる多重防御
3. **データ保護**: 保存時・転送時データの暗号化
4. **監査可能性**: すべてのアクセス・操作をログ記録
5. **自動化**: セキュリティ設定の自動化・標準化
6. **コンプライアンス**: AWS Well-Architected Security Pillarに準拠

### 脅威モデル
本プロジェクトで想定する主要な脅威：
- 不正アクセス（外部からのAPI攻撃）
- データ漏洩（データベース・ログからの情報流出）  
- サービス妨害攻撃（DDoS等）
- 内部脅威（誤設定による情報露出）
- 供給チェーン攻撃（コンテナイメージ改ざん等）

---

##  ネットワークセキュリティ

### 1. VPCセキュリティ設計

#### ネットワーク分離
```
Internet Gateway
      │
┌─────▼─────┐
│Public Subnet│ ← ALB配置
│10.0.1.0/24 │
└─────┬─────┘
      │
┌─────▼─────┐
│Private     │ ← ECS Tasks配置
│Subnet      │   (インターネット直接アクセス不可)
│10.0.11.0/24│
└───────────┘
```

#### Network ACL設計
```json
{
  "NetworkAcl": {
    "VpcId": "vpc-xxxxxxxx",
    "Rules": [
      {
        "RuleNumber": 100,
        "Protocol": "6",
        "RuleAction": "allow", 
        "CidrBlock": "0.0.0.0/0",
        "PortRange": {
          "From": 80,
          "To": 80
        }
      },
      {
        "RuleNumber": 110,
        "Protocol": "6",
        "RuleAction": "allow",
        "CidrBlock": "0.0.0.0/0", 
        "PortRange": {
          "From": 443,
          "To": 443
        }
      },
      {
        "RuleNumber": 32766,
        "Protocol": "-1",
        "RuleAction": "deny",
        "CidrBlock": "0.0.0.0/0"
      }
    ]
  }
}
```

### 2. セキュリティグループ設計

#### 階層化セキュリティグループ
| 層 | セキュリティグループ | 許可通信 |
|----|--------------------|----------|
| Web層 | ALB-SG | Internet → ALB:80,443 |
| App層 | ECS-SG | ALB-SG → ECS:8000 |  
| Data層 | - | ECS-SG → DynamoDB (IAM制御) |

#### ALBセキュリティグループ詳細
```json
{
  "GroupName": "portfolio-alb-sg",
  "Description": "ALB security group with restricted access",
  "VpcId": "vpc-xxxxxxxx",
  "SecurityGroupRules": [
    {
      "Direction": "Ingress",
      "IpProtocol": "tcp", 
      "FromPort": 80,
      "ToPort": 80,
      "CidrIpv4": "0.0.0.0/0",
      "Description": "HTTP from internet"
    },
    {
      "Direction": "Ingress",
      "IpProtocol": "tcp",
      "FromPort": 443, 
      "ToPort": 443,
      "CidrIpv4": "0.0.0.0/0",
      "Description": "HTTPS from internet"
    }
  ]
}
```

#### ECSセキュリティグループ詳細  
```json
{
  "GroupName": "portfolio-ecs-sg",
  "Description": "ECS tasks security group",
  "VpcId": "vpc-xxxxxxxx",
  "SecurityGroupRules": [
    {
      "Direction": "Ingress",
      "IpProtocol": "tcp",
      "FromPort": 8000,
      "ToPort": 8000,
      "ReferencedGroupId": "sg-alb-xxxxxxxx",
      "Description": "API access from ALB only"
    },
    {
      "Direction": "Egress",
      "IpProtocol": "tcp",
      "FromPort": 443,
      "ToPort": 443, 
      "CidrIpv4": "0.0.0.0/0",
      "Description": "HTTPS for AWS API calls"
    },
    {
      "Direction": "Egress",
      "IpProtocol": "tcp",
      "FromPort": 80,
      "ToPort": 80,
      "CidrIpv4": "0.0.0.0/0", 
      "Description": "HTTP for package downloads"
    }
  ]
}
```

---

##  アイデンティティ・アクセス管理 (IAM)

### 1. IAMロール設計

#### 役割別IAMロール
| ロール名 | 用途 | 付与対象 |
|----------|------|----------|
| ecsTaskRole | ECS Task実行時の権限 | ECS Tasks |
| ecsTaskExecutionRole | ECS Task起動時の権限 | ECS Service |
| githubActionsRole | CI/CD実行権限 | GitHub Actions |
| adminRole | 管理作業用権限 | 開発者 |

#### ECS Task Role詳細
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem", 
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-users",
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-users/index/*",
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-metrics",
        "arn:aws:dynamodb:ap-northeast-1:*:table/portfolio-metrics/index/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-1"
        }
      }
    },
    {
      "Sid": "CloudWatchLogs", 
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "arn:aws:logs:ap-northeast-1:*:log-group:/aws/ecs/portfolio-api:*"
      ]
    }
  ]
}
```

#### ECS Task Execution Role詳細
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAccess",
      "Effect": "Allow", 
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-northeast-1"
        }
      }
    },
    {
      "Sid": "CloudWatchLogsManagement",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup", 
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "arn:aws:logs:ap-northeast-1:*:log-group:/aws/ecs/*"
      ]
    }
  ]
}
```

### 2. リソースベースポリシー

#### S3バケットポリシー（CloudFrontアクセス用）
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::portfolio-static-website-bucket/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::account:distribution/DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

---

##  データ保護

### 1. 暗号化設計

#### 保存時暗号化
| サービス | 暗号化方式 | キー管理 |
|----------|------------|----------|
| DynamoDB | SSE | AWS Managed Keys |
| S3 | SSE-S3 | AWS Managed Keys |
| ECR | AES-256 | AWS Managed Keys |
| CloudWatch Logs | SSE | AWS Managed Keys |
| EBS | デフォルト暗号化 | AWS Managed Keys |

#### 転送時暗号化
| 通信経路 | プロトコル | 証明書 |
|----------|------------|--------|
| Client → ALB | HTTPS | AWS Certificate Manager |
| ALB → ECS | HTTP (VPC内) | - |
| ECS → DynamoDB | HTTPS | AWS SDK |
| ECS → CloudWatch | HTTPS | AWS SDK |

#### DynamoDB暗号化設定
```json
{
  "TableName": "portfolio-users",
  "SSESpecification": {
    "Enabled": true,
    "SSEType": "AES256",
    "KMSMasterKeyId": "alias/aws/dynamodb"
  }
}
```

#### S3暗号化設定
```json
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }
  ]
}
```

### 2. データ分類・取扱い

#### データ分類
| 分類 | 種類 | 暗号化 | 保持期間 | アクセス制御 |
|------|------|--------|----------|--------------|
| 公開データ | 静的Web | SSE-S3 | 無制限 | 一般公開 |
| アプリデータ | ユーザー情報 | SSE | 1年 | 認証必須 |
| ログデータ | アクセス・エラー | SSE | 30日 | 管理者のみ |
| 機密データ | 設定情報 | SSE | - | 管理者のみ |

---

##  アプリケーションセキュリティ

### 1. APIセキュリティ

#### 入力検証
```python
# FastAPI Pydantic modelによる入力検証例
from pydantic import BaseModel, EmailStr, Field
import re

class UserCreateRequest(BaseModel):
    username: str = Field(
        min_length=3, 
        max_length=50,
        regex="^[a-zA-Z0-9_]+$"
    )
    email: EmailStr
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username contains invalid characters')
        return v
```

#### レート制限設計
```python
# API レート制限設定例
RATE_LIMITS = {
    "/api/users": "100/minute",
    "/api/metrics": "1000/minute", 
    "/health": "unlimited",
    "default": "60/minute"
}
```

#### セキュリティヘッダー設定
```python
# FastAPI セキュリティヘッダー設定
from fastapi.security import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.portfolio-aws.com", "localhost"]
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

### 2. コンテナセキュリティ

#### ベースイメージセキュリティ
```dockerfile
# セキュアなベースイメージの使用
FROM python:3.11-slim

# 非rootユーザーでの実行
RUN useradd --create-home --shell /bin/bash app
USER app

# セキュリティ更新の適用
RUN apt-get update && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

#### ECRイメージスキャン設定
```json
{
  "repositoryName": "portfolio-api",
  "imageScanningConfiguration": {
    "scanOnPush": true
  },
  "imageTagMutability": "IMMUTABLE"
}
```

---

##  ログ・監視セキュリティ

### 1. セキュリティログ設計

#### ログ種別と内容
| ログ種別 | ログ内容 | 保持期間 | 監視レベル |
|----------|----------|----------|------------|
| API Access | リクエスト・レスポンス情報 | 30日 | INFO |
| Authentication | 認証成功・失敗 | 90日 | WARN |
| Authorization | 認可失敗 | 90日 | ERROR |
| Data Access | DB操作履歴 | 30日 | INFO |
| Security Events | 不正アクセス試行 | 1年 | CRITICAL |

#### 構造化ログ形式
```json
{
  "timestamp": "2025-08-23T10:00:00Z",
  "level": "INFO",
  "service": "portfolio-api",
  "event_type": "api_access",
  "user_id": "user_12345",
  "endpoint": "/api/users",
  "method": "GET", 
  "status_code": 200,
  "response_time_ms": 150,
  "ip_address": "203.0.113.1",
  "user_agent": "Mozilla/5.0...",
  "request_id": "req-abc123"
}
```

### 2. セキュリティ監視

#### CloudWatch Alarms設定
```json
[
  {
    "AlarmName": "HighErrorRate",
    "MetricName": "4xxError",
    "Namespace": "AWS/ApplicationELB", 
    "Statistic": "Sum",
    "Threshold": 10,
    "Period": 300,
    "EvaluationPeriods": 1,
    "ComparisonOperator": "GreaterThanThreshold"
  },
  {
    "AlarmName": "UnauthorizedAccess",
    "MetricName": "401ErrorCount",
    "Namespace": "Portfolio/API",
    "Threshold": 5,
    "Period": 300,
    "EvaluationPeriods": 1, 
    "ComparisonOperator": "GreaterThanThreshold"
  }
]
```

---

##  インシデント対応

### 1. セキュリティインシデント分類

#### インシデントレベル
| レベル | 定義 | 対応時間 | 対応者 |
|--------|------|----------|--------|
| Critical | データ漏洩、システム侵害 | 1時間以内 | 管理者 |
| High | 不正アクセス試行、DDoS | 4時間以内 | 管理者 |
| Medium | 設定不備、脆弱性発見 | 1日以内 | 開発者 |
| Low | ログ異常、監視アラート | 1週間以内 | 開発者 |

### 2. 対応手順

#### Critical/Highレベル対応フロー
1. **即時対応** (15分以内)
   - 影響範囲の特定
   - 攻撃の遮断（ALB/Security Group更新）
   - 関係者への緊急連絡

2. **調査・封じ込め** (1時間以内)  
   - ログ分析による原因特定
   - 追加的な封じ込め措置
   - 証跡の保全

3. **復旧・事後対応** (4時間以内)
   - システムの復旧
   - 脆弱性の修正
   - 監視強化

#### 緊急時コマンド
```bash
# ALBからの全トラフィック遮断
aws elbv2 modify-listener --listener-arn <ARN> \
  --default-actions Type=fixed-response,FixedResponseConfig='{StatusCode=503}'

# ECS Service停止
aws ecs update-service --cluster portfolio-cluster \
  --service portfolio-api-service --desired-count 0

# Security Group緊急更新（全アクセス拒否）
aws ec2 revoke-security-group-ingress --group-id sg-xxxxxxxx \
  --protocol all --port -1 --cidr 0.0.0.0/0
```

---

##  セキュリティチェックリスト

### デプロイ前チェック
- [ ] IAMロール最小権限確認
- [ ] セキュリティグループ設定確認  
- [ ] 暗号化設定有効化確認
- [ ] ログ設定動作確認
- [ ] 脆弱性スキャン実行
- [ ] 設定の文書化完了

### 運用チェック（月次）
- [ ] アクセスログ分析
- [ ] 脆弱性スキャン結果レビュー
- [ ] IAM権限レビュー
- [ ] セキュリティパッチ適用状況確認
- [ ] バックアップ動作確認
- [ ] インシデント対応訓練実施

### 年次レビュー
- [ ] セキュリティ設計全体見直し
- [ ] 脅威モデル更新
- [ ] セキュリティポリシー更新
- [ ] コンプライアンス確認

---

##  参考資料・標準

### AWS セキュリティベストプラクティス
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [AWS Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/)

### セキュリティフレームワーク
- NIST Cybersecurity Framework
- ISO 27001/27002
- OWASP Top 10

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**次回更新予定**: セキュリティ設定実装完了後
