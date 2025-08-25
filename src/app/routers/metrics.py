"""
Metrics Router
メトリクス管理エンドポイント
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query

from app.models.metric import (
    MetricCreate, MetricUpdate, MetricResponse, 
    MetricListResponse, MetricSummary, MetricStatus
)
from app.dependencies import get_metrics_table
from app.services.metric_service import MetricService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics", response_model=MetricListResponse)
async def get_metrics(
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
    offset: int = Query(default=0, ge=0, description="オフセット"),
    device_id: Optional[str] = Query(default=None, description="デバイスIDフィルター"),
    status: Optional[MetricStatus] = Query(default=None, description="ステータスフィルター"),
    metrics_table=Depends(get_metrics_table)
) -> MetricListResponse:
    """
    メトリクス一覧取得
    
    Args:
        limit: 取得件数 (1-100)
        offset: オフセット
        device_id: デバイスIDでフィルター
        status: ステータスでフィルター
        
    Returns:
        メトリクス一覧
    """
    try:
        metric_service = MetricService(metrics_table)
        result = await metric_service.get_metrics(
            limit=limit, 
            offset=offset,
            device_id=device_id,
            status=status
        )
        return result
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="メトリクス一覧の取得に失敗しました"
        )


@router.get("/metrics/latest", response_model=List[MetricResponse])
async def get_latest_metrics(
    device_id: Optional[str] = Query(default=None, description="デバイスIDフィルター"),
    limit: int = Query(default=10, ge=1, le=50, description="取得件数"),
    metrics_table=Depends(get_metrics_table)
) -> List[MetricResponse]:
    """
    最新メトリクス取得
    
    Args:
        device_id: デバイスIDフィルター
        limit: 取得件数
        
    Returns:
        最新のメトリクス一覧
    """
    try:
        metric_service = MetricService(metrics_table)
        result = await metric_service.get_latest_metrics(
            device_id=device_id,
            limit=limit
        )
        return result
        
    except Exception as e:
        logger.error(f"Failed to get latest metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="最新メトリクスの取得に失敗しました"
        )


@router.get("/metrics/summary", response_model=List[MetricSummary])
async def get_metrics_summary(
    device_id: Optional[str] = Query(default=None, description="デバイスIDフィルター"),
    metrics_table=Depends(get_metrics_table)
) -> List[MetricSummary]:
    """
    メトリクス集計情報取得
    
    Args:
        device_id: デバイスIDフィルター
        
    Returns:
        メトリクス集計情報
    """
    try:
        metric_service = MetricService(metrics_table)
        result = await metric_service.get_metrics_summary(device_id=device_id)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="メトリクス集計の取得に失敗しました"
        )


@router.get("/metrics/{metric_id}", response_model=MetricResponse)
async def get_metric(
    metric_id: str,
    metrics_table=Depends(get_metrics_table)
) -> MetricResponse:
    """
    メトリクス詳細取得
    
    Args:
        metric_id: メトリクスID
        
    Returns:
        メトリクス詳細情報
    """
    try:
        metric_service = MetricService(metrics_table)
        metric = await metric_service.get_metric(metric_id)
        
        if not metric:
            raise HTTPException(
                status_code=404,
                detail="メトリクスが見つかりません"
            )
            
        return metric
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metric {metric_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="メトリクス情報の取得に失敗しました"
        )


@router.post("/metrics", response_model=MetricResponse, status_code=201)
async def create_metric(
    metric_data: MetricCreate,
    metrics_table=Depends(get_metrics_table)
) -> MetricResponse:
    """
    メトリクス作成
    
    Args:
        metric_data: メトリクス作成データ
        
    Returns:
        作成されたメトリクス情報
    """
    try:
        metric_service = MetricService(metrics_table)
        new_metric = await metric_service.create_metric(metric_data)
        return new_metric
        
    except Exception as e:
        logger.error(f"Failed to create metric: {e}")
        raise HTTPException(
            status_code=500,
            detail="メトリクスの作成に失敗しました"
        )


@router.put("/metrics/{metric_id}", response_model=MetricResponse)
async def update_metric(
    metric_id: str,
    metric_data: MetricUpdate,
    metrics_table=Depends(get_metrics_table)
) -> MetricResponse:
    """
    メトリクス更新
    
    Args:
        metric_id: メトリクスID
        metric_data: 更新データ
        
    Returns:
        更新されたメトリクス情報
    """
    try:
        metric_service = MetricService(metrics_table)
        
        # メトリクス存在確認
        existing_metric = await metric_service.get_metric(metric_id)
        if not existing_metric:
            raise HTTPException(
                status_code=404,
                detail="メトリクスが見つかりません"
            )
        
        # 更新実行
        updated_metric = await metric_service.update_metric(metric_id, metric_data)
        return updated_metric
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update metric {metric_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="メトリクス情報の更新に失敗しました"
        )


@router.delete("/metrics/{metric_id}")
async def delete_metric(
    metric_id: str,
    metrics_table=Depends(get_metrics_table)
) -> dict:
    """
    メトリクス削除
    
    Args:
        metric_id: メトリクスID
        
    Returns:
        削除結果
    """
    try:
        metric_service = MetricService(metrics_table)
        
        # メトリクス存在確認
        existing_metric = await metric_service.get_metric(metric_id)
        if not existing_metric:
            raise HTTPException(
                status_code=404,
                detail="メトリクスが見つかりません"
            )
        
        # 削除実行
        await metric_service.delete_metric(metric_id)
        
        return {
            "message": "メトリクスを削除しました",
            "metric_id": metric_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete metric {metric_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="メトリクスの削除に失敗しました"
        )