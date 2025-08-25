"""
Portfolio AWS Infrastructure - FastAPI Main Application
ポートフォリオ用AWS環境のメインAPIアプリケーション

Author: Rin Nakahata
Created: 2025-08-25
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.routers import health, users, metrics
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.dependencies import get_dynamodb_client

# ログ設定
setup_logging()
logger = logging.getLogger(__name__)

# 設定読み込み
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    logger.info("Starting Portfolio API application...")
    
    # 起動時の処理
    try:
        # DynamoDB接続テスト
        dynamodb = get_dynamodb_client()
        logger.info("DynamoDB connection established")
    except Exception as e:
        logger.error(f"Failed to connect to DynamoDB: {e}")
        raise
    
    yield
    
    # 終了時の処理
    logger.info("Shutting down Portfolio API application...")


# FastAPIアプリケーション作成
app = FastAPI(
    title="Portfolio AWS Infrastructure API",
    description="AWS環境構築スキル証明用のポートフォリオAPI",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# ルーター登録
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Portfolio AWS Infrastructure API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs" if settings.DEBUG else "unavailable in production"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP例外ハンドラー"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": settings.get_current_timestamp()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """一般例外ハンドラー"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": settings.get_current_timestamp()
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )