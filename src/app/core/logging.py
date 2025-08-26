"""
Portfolio API Logging Configuration
ログ設定
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path

# ログディレクトリの作成
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


class StructuredFormatter(logging.Formatter):
    """構造化ログフォーマッター"""
    
    def format(self, record: logging.LogRecord) -> str:
        """ログレコードを構造化JSON形式に変換"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread
        }
        
        # 追加フィールドがある場合
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # 例外情報がある場合
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # リクエスト情報がある場合
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'ip_address'):
            log_entry["ip_address"] = record.ip_address
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ColoredFormatter(logging.Formatter):
    """カラー付きコンソールフォーマッター（開発用）"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # シアン
        'INFO': '\033[32m',     # 緑
        'WARNING': '\033[33m',  # 黄
        'ERROR': '\033[31m',    # 赤
        'CRITICAL': '\033[35m', # マゼンタ
        'RESET': '\033[0m'      # リセット
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        formatted = super().format(record)
        return f"{color}{formatted}{reset}"


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_structured: bool = True
) -> None:
    """ログ設定の初期化"""
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # コンソールハンドラー
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        if enable_structured:
            console_formatter = StructuredFormatter()
        else:
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # ファイルハンドラー
    if enable_file and log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        if enable_structured:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # 特定のライブラリのログレベルを調整
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
) -> None:
    """コンテキスト情報付きでログを出力"""
    extra_fields = kwargs.copy()
    
    # ログレベルに応じてメソッドを呼び出し
    log_method = getattr(logger, level.lower())
    log_method(message, extra={"extra_fields": extra_fields})


def log_request(
    logger: logging.Logger,
    request_id: str,
    method: str,
    path: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs
) -> None:
    """リクエストログを出力"""
    extra_fields = {
        "request_id": request_id,
        "method": method,
        "path": path,
        "user_id": user_id,
        "ip_address": ip_address,
        **kwargs
    }
    
    logger.info(
        f"Request: {method} {path}",
        extra={"extra_fields": extra_fields}
    )


def log_response(
    logger: logging.Logger,
    request_id: str,
    status_code: int,
    response_time: float,
    **kwargs
) -> None:
    """レスポンスログを出力"""
    extra_fields = {
        "request_id": request_id,
        "status_code": status_code,
        "response_time": response_time,
        **kwargs
    }
    
    level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
    log_method = getattr(logger, level)
    
    log_method(
        f"Response: {status_code} ({response_time:.3f}s)",
        extra={"extra_fields": extra_fields}
    )


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table_name: str,
    duration: float,
    success: bool,
    **kwargs
) -> None:
    """データベース操作ログを出力"""
    extra_fields = {
        "operation": operation,
        "table_name": table_name,
        "duration": duration,
        "success": success,
        **kwargs
    }
    
    level = "info" if success else "error"
    log_method = getattr(logger, level)
    
    log_method(
        f"Database {operation} on {table_name}: {'success' if success else 'failed'} ({duration:.3f}s)",
        extra={"extra_fields": extra_fields}
    )


# デフォルト設定
setup_logging(
    log_level="INFO",
    log_file="logs/portfolio-api.log",
    enable_console=True,
    enable_file=True,
    enable_structured=True
)