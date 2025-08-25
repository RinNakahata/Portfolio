"""
FastAPI Dependencies
共通の依存関係管理
"""

import logging
from functools import lru_cache

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_dynamodb_client():
    """
    DynamoDBクライアントを取得
    キャッシュ機能付きで、一度作成されたクライアントを再利用
    """
    try:
        aws_config = settings.get_aws_config()
        client = boto3.client('dynamodb', **aws_config)
        
        # 接続テスト
        client.list_tables()
        logger.info("DynamoDB client created successfully")
        return client
        
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials")
        raise
    except Exception as e:
        logger.error(f"Failed to create DynamoDB client: {e}")
        raise


@lru_cache()
def get_dynamodb_resource():
    """
    DynamoDB高レベルリソースを取得
    より使いやすいAPI用
    """
    try:
        aws_config = settings.get_aws_config()
        resource = boto3.resource('dynamodb', **aws_config)
        
        logger.info("DynamoDB resource created successfully")
        return resource
        
    except Exception as e:
        logger.error(f"Failed to create DynamoDB resource: {e}")
        raise


def get_users_table():
    """Users DynamoDBテーブルを取得"""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.DYNAMODB_USERS_TABLE)


def get_metrics_table():
    """Metrics DynamoDBテーブルを取得"""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.DYNAMODB_METRICS_TABLE)