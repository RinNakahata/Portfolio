"""
Metrics Data Models
メトリクスデータモデル
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class MetricStatus(str, Enum):
    """メトリクスステータス"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class MetricBase(BaseModel):
    """メトリクス基本モデル"""
    device_id: str = Field(..., description="デバイスID")
    metric_name: str = Field(..., description="メトリクス名")
    value: float = Field(..., description="メトリクス値")
    unit: str = Field(..., description="単位")
    status: MetricStatus = Field(MetricStatus.ACTIVE, description="ステータス")
    metadata: Optional[Dict[str, Any]] = Field(None, description="追加メタデータ")


class MetricCreate(MetricBase):
    """メトリクス作成用モデル"""
    pass


class MetricUpdate(BaseModel):
    """メトリクス更新用モデル"""
    value: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[MetricStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricResponse(MetricBase):
    """メトリクスレスポンス用モデル"""
    metric_id: str = Field(..., description="メトリクスID")
    timestamp: datetime = Field(..., description="タイムスタンプ")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    
    class Config:
        from_attributes = True


class MetricListResponse(BaseModel):
    """メトリクス一覧レスポンス用モデル"""
    metrics: list[MetricResponse]
    total_count: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True


class MetricSummary(BaseModel):
    """メトリクス集計用モデル"""
    device_id: str
    metric_name: str
    total_count: int
    avg_value: float
    min_value: float
    max_value: float
    latest_timestamp: datetime
    latest_value: float
    latest_status: MetricStatus