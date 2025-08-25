"""
Health Check Router
ヘルスチェック用エンドポイント
"""

import logging
import time
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings
from app.dependencies import get_dynamodb_client

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    基本的なヘルスチェック
    アプリケーションの稼働状況を確認
    """
    return {
        "status": "healthy",
        "timestamp": settings.get_current_timestamp(),
        "version": settings.APP_VERSION,
        "service": "portfolio-api"
    }


@router.get("/health/detailed")
async def detailed_health_check(
    dynamodb_client = Depends(get_dynamodb_client)
) -> Dict[str, Any]:
    """
    詳細なヘルスチェック
    外部依存関係を含めた健全性確認
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": settings.get_current_timestamp(),
        "version": settings.APP_VERSION,
        "service": "portfolio-api",
        "checks": {}
    }
    
    # DynamoDB接続チェック
    try:
        # usersテーブルの存在確認
        response = dynamodb_client.describe_table(
            TableName=settings.DYNAMODB_USERS_TABLE
        )
        health_status["checks"]["dynamodb_users"] = {
            "status": "healthy",
            "table_status": response.get("Table", {}).get("TableStatus"),
            "message": "Users table accessible"
        }
    except ClientError as e:
        logger.warning(f"DynamoDB users table check failed: {e}")
        health_status["checks"]["dynamodb_users"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Users table not accessible"
        }
        health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Unexpected error in DynamoDB users check: {e}")
        health_status["checks"]["dynamodb_users"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Unexpected error"
        }
        health_status["status"] = "unhealthy"
    
    # Metricsテーブルチェック
    try:
        response = dynamodb_client.describe_table(
            TableName=settings.DYNAMODB_METRICS_TABLE
        )
        health_status["checks"]["dynamodb_metrics"] = {
            "status": "healthy",
            "table_status": response.get("Table", {}).get("TableStatus"),
            "message": "Metrics table accessible"
        }
    except ClientError as e:
        logger.warning(f"DynamoDB metrics table check failed: {e}")
        health_status["checks"]["dynamodb_metrics"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Metrics table not accessible"
        }
        health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Unexpected error in DynamoDB metrics check: {e}")
        health_status["checks"]["dynamodb_metrics"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Unexpected error"
        }
        health_status["status"] = "unhealthy"
    
    # レスポンス時間追加
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_status


@router.get("/health/db")
async def database_health_check(
    dynamodb_client = Depends(get_dynamodb_client)
) -> Dict[str, Any]:
    """
    データベース専用ヘルスチェック
    DynamoDBの接続と基本操作を確認
    """
    try:
        # テーブル一覧取得テスト
        response = dynamodb_client.list_tables()
        tables = response.get("TableNames", [])
        
        return {
            "status": "healthy",
            "timestamp": settings.get_current_timestamp(),
            "database": "DynamoDB",
            "region": settings.AWS_REGION,
            "tables_found": len(tables),
            "expected_tables": [
                settings.DYNAMODB_USERS_TABLE,
                settings.DYNAMODB_METRICS_TABLE
            ],
            "message": "Database connection successful"
        }
        
    except ClientError as e:
        logger.error(f"DynamoDB connection failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "DynamoDB",
                "error": str(e),
                "message": "Database connection failed"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "database": "DynamoDB", 
                "error": str(e),
                "message": "Unexpected database error"
            }
        )