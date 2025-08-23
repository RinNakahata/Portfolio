# インフラ構成詳細設計書

##  文書情報

- **作成日**: 2025-08-23
- **バージョン**: v1.0
- **対象環境**: AWS (ap-northeast-1)
- **作成者**: Rin Nakahata
- **最終更新**: 2025-08-23

---

##  設計方針

### インフラ設計原則
1. **可用性**: Multi-AZ構成による冗長化
2. **セキュリティ**: Private Subnet でのアプリケーション実行
3. **スケーラビリティ**: 自動スケーリング対応
4. **コスト効率**: 無料利用枠の最大活用
5. **運用性**: CloudWatch による統合監視
6. **自動化**: Terraform による Infrastructure as Code

---

##  ネットワーク設計

### VPC構成

#### VPC設定
| 項目 | 設定値 | 説明 |
|------|--------|------|
| VPC CIDR | 10.0.0.0/16 | プライベートネットワーク |
| DNS Resolution | 有効 | 内部DNSの有効化 |
| DNS Hostnames | 有効 | インスタンスのホスト名解決 |
| Tenancy | default | 共有テナンシー |

#### Subnet設計

##### Public Subnet
| Subnet | AZ | CIDR | 用途 |
|--------|----|----- |------|
| public-1a | ap-northeast-1a | 10.0.1.0/24 | ALB, NAT Gateway |
| public-1c | ap-northeast-1c | 10.0.2.0/24 | ALB |

##### Private Subnet  
| Subnet | AZ | CIDR | 用途 |
|--------|----|----- |------|
| private-1a | ap-northeast-1a | 10.0.11.0/24 | ECS Tasks |
| private-1c | ap-northeast-1c | 10.0.12.0/24 | ECS Tasks |

#### ルーティング設計

##### Public Route Table
| 宛先 | ターゲット | 説明 |
|------|------------|------|
| 10.0.0.0/16 | Local | VPC内通信 |
| 0.0.0.0/0 | Internet Gateway | インターネット通信 |

##### Private Route Table
| 宛先 | ターゲット | 説明 |
|------|------------|------|
| 10.0.0.0/16 | Local | VPC内通信 |
| 0.0.0.0/0 | NAT Gateway | インターネット通信（送信のみ） |

### セキュリティグループ設計

#### ALB Security Group
```json
{
  "GroupName": "portfolio-alb-sg",
  "Description": "Security group for Application Load Balancer",
  "VpcId": "vpc-xxxxxxxx",
  "SecurityGroupRules": [
    {
      "Direction": "Ingress",
      "IpProtocol": "tcp",
      "FromPort": 80,
      "ToPort": 80,
      "CidrIpv4": "0.0.0.0/0",
      "Description": "HTTP access from anywhere"
    },
    {
      "Direction": "Ingress", 
      "IpProtocol": "tcp",
      "FromPort": 443,
      "ToPort": 443,
      "CidrIpv4": "0.0.0.0/0",
      "Description": "HTTPS access from anywhere"
    },
    {
      "Direction": "Egress",
      "IpProtocol": "-1",
      "CidrIpv4": "0.0.0.0/0",
      "Description": "All outbound traffic"
    }
  ]
}
```

#### ECS Security Group
```json
{
  "GroupName": "portfolio-ecs-sg",
  "Description": "Security group for ECS tasks",
  "VpcId": "vpc-xxxxxxxx", 
  "SecurityGroupRules": [
    {
      "Direction": "Ingress",
      "IpProtocol": "tcp",
      "FromPort": 8000,
      "ToPort": 8000,
      "ReferencedGroupId": "sg-alb-xxxxxxxx",
      "Description": "HTTP access from ALB"
    },
    {
      "Direction": "Egress",
      "IpProtocol": "-1",
      "CidrIpv4": "0.0.0.0/0", 
      "Description": "All outbound traffic"
    }
  ]
}
```

---

##  コンテナ基盤設計

### ECS Cluster設計

#### Cluster構成
| 項目 | 設定値 | 説明 |
|------|--------|------|
| Cluster名 | portfolio-cluster | ECSクラスター名 |
| Capacity Provider | FARGATE | サーバーレスコンテナ |
| Default Strategy | FARGATE 100% | Fargate優先実行 |

#### Task Definition設計
```json
{
  "family": "portfolio-api",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "api-container",
      "image": "account.dkr.ecr.ap-northeast-1.amazonaws.com/portfolio-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp",
          "name": "api-port"
        }
      ],
      "environment": [
        {
          "name": "ENV",
          "value": "production"
        },
        {
          "name": "AWS_REGION", 
          "value": "ap-northeast-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/aws/ecs/portfolio-api",
          "awslogs-region": "ap-northeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### Service設計
```json
{
  "serviceName": "portfolio-api-service",
  "cluster": "portfolio-cluster", 
  "taskDefinition": "portfolio-api",
  "desiredCount": 1,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": [
        "subnet-private-1a",
        "subnet-private-1c"  
      ],
      "securityGroups": ["sg-ecs-xxxxxxxx"],
      "assignPublicIp": "DISABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:ap-northeast-1:account:targetgroup/portfolio-tg",
      "containerName": "api-container",
      "containerPort": 8000
    }
  ],
  "healthCheckGracePeriodSeconds": 300,
  "serviceTags": [
    {
      "key": "Project",
      "value": "Portfolio"
    }
  ]
}
```

### Auto Scaling設計

#### Service Auto Scaling
```json
{
  "ServiceNamespace": "ecs",
  "ResourceId": "service/portfolio-cluster/portfolio-api-service",
  "ScalableDimension": "ecs:service:DesiredCount",
  "MinCapacity": 1,
  "MaxCapacity": 3,
  "ScalingPolicies": [
    {
      "PolicyName": "cpu-scale-out",
      "PolicyType": "TargetTrackingScaling", 
      "TargetTrackingScalingPolicyConfiguration": {
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
          "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
        },
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
      }
    }
  ]
}
```

---

##  ロードバランサー設計

### Application Load Balancer

#### ALB設定
| 項目 | 設定値 | 説明 |
|------|--------|------|
| 名前 | portfolio-alb | ALB名 |
| スキーム | internet-facing | インターネット向け |
| IP Address Type | ipv4 | IPv4のみ |
| Subnets | public-1a, public-1c | パブリックサブネット |
| Security Groups | alb-sg | ALBセキュリティグループ |

#### Target Group設定
```json
{
  "Name": "portfolio-tg",
  "Protocol": "HTTP",
  "Port": 8000,
  "VpcId": "vpc-xxxxxxxx",
  "TargetType": "ip",
  "HealthCheckEnabled": true,
  "HealthCheckProtocol": "HTTP",
  "HealthCheckPath": "/health",
  "HealthCheckIntervalSeconds": 30,
  "HealthCheckTimeoutSeconds": 5,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3,
  "Matcher": {
    "HttpCode": "200"
  }
}
```

#### Listener設定
```json
{
  "LoadBalancerArn": "arn:aws:elasticloadbalancing:ap-northeast-1:account:loadbalancer/app/portfolio-alb",
  "Protocol": "HTTP",
  "Port": 80,
  "DefaultActions": [
    {
      "Type": "forward",
      "TargetGroupArn": "arn:aws:elasticloadbalancing:ap-northeast-1:account:targetgroup/portfolio-tg"
    }
  ]
}
```

---

##  コンテナレジストリ設計

### ECR Repository

#### Repository設定
```json
{
  "repositoryName": "portfolio-api",
  "imageScanningConfiguration": {
    "scanOnPush": true
  },
  "imageTagMutability": "MUTABLE",
  "encryptionConfiguration": {
    "encryptionType": "AES256"
  },
  "lifecyclePolicy": {
    "lifecyclePolicyText": "{\"rules\":[{\"rulePriority\":1,\"selection\":{\"tagStatus\":\"untagged\",\"countType\":\"sinceImagePushed\",\"countUnit\":\"days\",\"countNumber\":1},\"action\":{\"type\":\"expire\"}}]}"
  }
}
```

---

##  CDN・静的ホスティング設計

### S3 Bucket設計

#### S3設定
```json
{
  "Bucket": "portfolio-static-website-bucket",
  "PublicAccessBlockConfiguration": {
    "BlockPublicAcls": false,
    "IgnorePublicAcls": false, 
    "BlockPublicPolicy": false,
    "RestrictPublicBuckets": false
  },
  "WebsiteConfiguration": {
    "IndexDocument": {
      "Suffix": "index.html"
    },
    "ErrorDocument": {
      "Key": "error.html"
    }
  },
  "CorsConfiguration": {
    "CorsRules": [
      {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "MaxAgeSeconds": 3600
      }
    ]
  }
}
```

### CloudFront設計

#### Distribution設定
```json
{
  "DistributionConfig": {
    "CallerReference": "portfolio-distribution-2025",
    "Comment": "Portfolio static website CDN",
    "Enabled": true,
    "Origins": [
      {
        "Id": "S3-portfolio-static-website",
        "DomainName": "portfolio-static-website-bucket.s3.ap-northeast-1.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ],
    "DefaultCacheBehavior": {
      "TargetOriginId": "S3-portfolio-static-website",
      "ViewerProtocolPolicy": "redirect-to-https",
      "TrustedSigners": {
        "Enabled": false
      },
      "ForwardedValues": {
        "QueryString": false,
        "Cookies": {
          "Forward": "none"
        }
      },
      "MinTTL": 0,
      "DefaultTTL": 86400,
      "MaxTTL": 31536000
    },
    "PriceClass": "PriceClass_All"
  }
}
```

---

##  監視・ログ設計

### CloudWatch Logs

#### Log Group設定
| Log Group名 | 保持期間 | 用途 |
|-------------|----------|------|
| `/aws/ecs/portfolio-api` | 30日 | ECSタスクログ |
| `/aws/elasticloadbalancing/app/portfolio-alb` | 30日 | ALBアクセスログ |

### CloudWatch Metrics

#### カスタムメトリクス
| メトリクス名 | 単位 | 説明 |
|--------------|------|------|
| `API/ResponseTime` | Milliseconds | API応答時間 |
| `API/RequestCount` | Count | API総リクエスト数 |
| `API/ErrorRate` | Percent | API エラー率 |

#### CloudWatch Alarms
```json
[
  {
    "AlarmName": "ECS-HighCPUUtilization",
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/ECS",
    "Statistic": "Average",
    "Dimensions": [
      {
        "Name": "ServiceName",
        "Value": "portfolio-api-service"
      },
      {
        "Name": "ClusterName", 
        "Value": "portfolio-cluster"
      }
    ],
    "Period": 300,
    "EvaluationPeriods": 2,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanThreshold"
  },
  {
    "AlarmName": "ALB-HighResponseTime",
    "MetricName": "TargetResponseTime", 
    "Namespace": "AWS/ApplicationELB",
    "Statistic": "Average",
    "Dimensions": [
      {
        "Name": "LoadBalancer",
        "Value": "app/portfolio-alb/xxxxx"
      }
    ],
    "Period": 300,
    "EvaluationPeriods": 2,
    "Threshold": 0.5,
    "ComparisonOperator": "GreaterThanThreshold"
  }
]
```

---

##  IAM設計

### ECS Task Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
      ]
    },
    {
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

### ECS Task Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow", 
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

---

##  コスト設計

### 予想月額コスト

| サービス | 設定 | 月額コスト（USD） |
|----------|------|------------------|
| ECS/Fargate | 0.25vCPU, 512MB, 24h稼働 | ~$8 |
| ALB | 基本料金 + LCU | ~$3 |
| NAT Gateway | 1つ、少量通信 | ~$5 |
| DynamoDB | オンデマンド、少量データ | ~$1 |
| S3 | 1GB、少量リクエスト | ~$1 |
| CloudFront | 少量転送 | ~$1 |
| CloudWatch | 基本メトリクス | ~$1 |
| **合計** | | **~$20** |

### コスト最適化策
1. **開発期間外停止**: ECS Serviceの停止
2. **NAT Gateway削除**: 開発時のみ作成
3. **ALB削除**: デモ時のみ起動
4. **ログ保持期間**: 短期間設定

---

##  デプロイ設計

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
    
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1
          
      - name: Build and push Docker image
        run: |
          docker build -t portfolio-api .
          docker tag portfolio-api:latest $ECR_REPOSITORY:latest
          docker push $ECR_REPOSITORY:latest
          
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster portfolio-cluster \
            --service portfolio-api-service \
            --force-new-deployment
```

### Blue/Green Deployment（将来拡張）
- **CodeDeploy**: ECS Blue/Green デプロイメント
- **Target Group切り替え**: 無停止デプロイ

---

##  災害復旧設計

### バックアップ戦略
- **DynamoDB**: Point-in-time Recovery
- **S3**: Cross-Region Replication（オプション）
- **ECR**: Multi-Region push（オプション）

### 復旧手順
1. **Terraform Apply**: インフラ再構築
2. **DynamoDB Restore**: データ復旧
3. **ECS Service再起動**: アプリケーション復旧

---

##  変更履歴

| バージョン | 日付 | 変更内容 |
|------------|------|----------|
| 1.0.0 | 2025-08-23 | 初版作成 |

---

**次回更新予定**: Phase 2 ECS/Fargate実装完了後
