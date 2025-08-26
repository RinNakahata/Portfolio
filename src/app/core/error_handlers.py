"""
Portfolio API Error Handlers
エラーハンドラー
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import PortfolioAPIException

logger = logging.getLogger(__name__)


async def portfolio_exception_handler(request: Request, exc: PortfolioAPIException) -> JSONResponse:
    """カスタム例外のハンドラー"""
    logger.error(f"PortfolioAPIException: {exc.message}", extra={
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method,
        "details": exc.details
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """バリデーションエラーのハンドラー"""
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "validation_errors": exc.errors()
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP例外のハンドラー"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}", extra={
        "path": request.url.path,
        "method": request.method,
        "status_code": exc.status_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": "HTTP_ERROR",
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {}
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """一般例外のハンドラー"""
    logger.error(f"Unexpected error: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method,
        "error_type": type(exc).__name__,
        "error_details": str(exc)
    }, exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {
                "message": "An unexpected error occurred"
            }
        }
    )


def register_exception_handlers(app):
    """例外ハンドラーをアプリケーションに登録"""
    app.add_exception_handler(PortfolioAPIException, portfolio_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
