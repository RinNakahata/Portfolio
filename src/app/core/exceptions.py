"""
Portfolio API Custom Exceptions
カスタム例外クラス
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any


class PortfolioAPIException(Exception):
    """ポートフォリオAPIの基本例外クラス"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """例外を辞書形式に変換"""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "status_code": self.status_code,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class ValidationException(PortfolioAPIException):
    """バリデーションエラーの例外"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", details=details)


class UserNotFoundException(PortfolioAPIException):
    """ユーザーが見つからない場合の例外"""
    
    def __init__(self, user_id: str):
        super().__init__(
            f"User not found: {user_id}", 
            status_code=404, 
            error_code="USER_NOT_FOUND",
            details={"user_id": user_id}
        )


class UserAlreadyExistsException(PortfolioAPIException):
    """ユーザーが既に存在する場合の例外"""
    
    def __init__(self, username: Optional[str] = None, email: Optional[str] = None):
        message = "User already exists"
        details = {}
        
        if username:
            details["username"] = username
        if email:
            details["email"] = email
            
        super().__init__(
            message, 
            status_code=409, 
            error_code="USER_ALREADY_EXISTS",
            details=details
        )


class MetricNotFoundException(PortfolioAPIException):
    """メトリクスが見つからない場合の例外"""
    
    def __init__(self, metric_id: str):
        super().__init__(
            f"Metric not found: {metric_id}", 
            status_code=404, 
            error_code="METRIC_NOT_FOUND",
            details={"metric_id": metric_id}
        )


class DeviceNotFoundException(PortfolioAPIException):
    """デバイスが見つからない場合の例外"""
    
    def __init__(self, device_id: str):
        super().__init__(
            f"Device not found: {device_id}", 
            status_code=404, 
            error_code="DEVICE_NOT_FOUND",
            details={"device_id": device_id}
        )


class DatabaseConnectionException(PortfolioAPIException):
    """データベース接続エラーの例外"""
    
    def __init__(self, operation: str, error: str):
        super().__init__(
            f"Database connection failed during {operation}: {error}", 
            status_code=503, 
            error_code="DATABASE_CONNECTION_ERROR",
            details={"operation": operation, "error": error}
        )


class DynamoDBException(PortfolioAPIException):
    """DynamoDB操作エラーの例外"""
    
    def __init__(self, operation: str, error: str, table_name: Optional[str] = None):
        details = {"operation": operation, "error": error}
        if table_name:
            details["table_name"] = table_name
            
        super().__init__(
            f"DynamoDB operation failed: {operation} - {error}", 
            status_code=500, 
            error_code="DYNAMODB_ERROR",
            details=details
        )


class AuthenticationException(PortfolioAPIException):
    """認証エラーの例外"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationException(PortfolioAPIException):
    """認可エラーの例外"""
    
    def __init__(self, message: str = "Insufficient permissions", required_permissions: Optional[list] = None):
        details = {}
        if required_permissions:
            details["required_permissions"] = required_permissions
            
        super().__init__(
            message, 
            status_code=403, 
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class RateLimitException(PortfolioAPIException):
    """レート制限エラーの例外"""
    
    def __init__(self, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
            
        super().__init__(
            "Rate limit exceeded", 
            status_code=429, 
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class ServiceUnavailableException(PortfolioAPIException):
    """サービス利用不可エラーの例外"""
    
    def __init__(self, service: str, error: str):
        super().__init__(
            f"Service {service} is unavailable: {error}", 
            status_code=503, 
            error_code="SERVICE_UNAVAILABLE",
            details={"service": service, "error": error}
        )


class InternalServerException(PortfolioAPIException):
    """内部サーバーエラーの例外"""
    
    def __init__(self, operation: str, error: str):
        super().__init__(
            f"Internal server error during {operation}: {error}", 
            status_code=500, 
            error_code="INTERNAL_SERVER_ERROR",
            details={"operation": operation, "error": error}
        )
