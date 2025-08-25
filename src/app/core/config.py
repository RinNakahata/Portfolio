"""
Portfolio API Configuration
設定管理モジュール
"""

import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # アプリケーション基本設定
    APP_NAME: str = "Portfolio AWS Infrastructure API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # AWS設定
    AWS_REGION: str = Field(default="ap-northeast-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # DynamoDB設定
    DYNAMODB_USERS_TABLE: str = Field(default="portfolio-users", env="DYNAMODB_USERS_TABLE")
    DYNAMODB_METRICS_TABLE: str = Field(default="portfolio-metrics", env="DYNAMODB_METRICS_TABLE")
    DYNAMODB_ENDPOINT_URL: Optional[str] = Field(default=None, env="DYNAMODB_ENDPOINT_URL")  # ローカル開発用
    
    # CORS設定
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "https://*.cloudfront.net"
        ],
        env="ALLOWED_ORIGINS"
    )
    
    # ログ設定
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # ヘルスチェック設定
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @staticmethod
    def get_current_timestamp() -> str:
        """現在のタイムスタンプを取得"""
        return datetime.now(timezone.utc).isoformat()
    
    def get_aws_config(self) -> dict:
        """AWS設定辞書を取得"""
        config = {
            "region_name": self.AWS_REGION
        }
        
        # 認証情報が環境変数にある場合のみ追加
        if self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY:
            config.update({
                "aws_access_key_id": self.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": self.AWS_SECRET_ACCESS_KEY
            })
        
        # ローカル開発用エンドポイント
        if self.DYNAMODB_ENDPOINT_URL:
            config["endpoint_url"] = self.DYNAMODB_ENDPOINT_URL
            
        return config


@lru_cache()
def get_settings() -> Settings:
    """設定インスタンスを取得（キャッシュ付き）"""
    return Settings()