"""
Metric Service
メトリクス管理ビジネスロジック
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from app.models.metric import (
    MetricCreate, MetricUpdate, MetricResponse, 
    MetricListResponse, MetricSummary, MetricStatus
)

logger = logging.getLogger(__name__)


class MetricService:
    """メトリクス管理サービス"""
    
    def __init__(self, metrics_table):
        self.metrics_table = metrics_table
    
    async def get_metrics(
        self, 
        limit: int = 10, 
        offset: int = 0,
        device_id: Optional[str] = None,
        status: Optional[MetricStatus] = None
    ) -> MetricListResponse:
        """メトリクス一覧取得"""
        try:
            # フィルター条件を構築
            filter_expression = None
            expression_attribute_values = {}
            
            if device_id:
                filter_expression = "device_id = :device_id"
                expression_attribute_values[':device_id'] = device_id
                
            if status:
                if filter_expression:
                    filter_expression += " AND #status = :status"
                else:
                    filter_expression = "#status = :status"
                expression_attribute_values[':status'] = status.value
                expression_attribute_values['#status'] = 'status'
            
            # DynamoDBからメトリクス一覧を取得
            scan_kwargs = {
                'Limit': limit
            }
            
            if filter_expression:
                scan_kwargs['FilterExpression'] = filter_expression
                scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values
                
            if filter_expression and '#status' in expression_attribute_values:
                scan_kwargs['ExpressionAttributeNames'] = {'#status': 'status'}
            
            # offsetがある場合は簡易的な実装
            if offset and offset > 0:
                response = self.metrics_table.scan()
                items = response.get('Items', [])
                if offset < len(items):
                    items = items[offset:offset + limit]
                else:
                    items = []
                count = len(items)
            else:
                response = self.metrics_table.scan(**scan_kwargs)
                items = response.get('Items', [])
                count = response.get('Count', 0)
            
            metrics = [MetricResponse(**item) for item in items]
            return MetricListResponse(
                metrics=metrics,
                total_count=count,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            raise
    
    async def get_latest_metrics(
        self, 
        device_id: Optional[str] = None,
        limit: int = 10
    ) -> List[MetricResponse]:
        """最新メトリクス取得"""
        try:
            if device_id:
                # 特定デバイスの最新メトリクス（timestamp-indexを使用）
                response = self.metrics_table.query(
                    IndexName='timestamp-index',
                    KeyConditionExpression='device_id = :device_id',
                    ExpressionAttributeValues={':device_id': device_id},
                    ScanIndexForward=False,  # 降順（最新順）
                    Limit=limit
                )
            else:
                # 全デバイスの最新メトリクス
                response = self.metrics_table.scan(
                    Limit=limit
                )
            
            items = response.get('Items', [])
            # タイムスタンプでソート（最新順）
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return [MetricResponse(**item) for item in items[:limit]]
        except Exception as e:
            logger.error(f"Failed to get latest metrics: {e}")
            raise
    
    async def get_metrics_summary(
        self, 
        device_id: Optional[str] = None
    ) -> List[MetricSummary]:
        """メトリクス集計取得"""
        try:
            # フィルター条件を構築
            filter_expression = None
            expression_attribute_values = {}
            
            if device_id:
                filter_expression = "device_id = :device_id"
                expression_attribute_values[':device_id'] = device_id
            
            # DynamoDBからメトリクスを取得
            scan_kwargs = {}
            if filter_expression:
                scan_kwargs['FilterExpression'] = filter_expression
                scan_kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
            response = self.metrics_table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            # デバイス別に集計
            device_summaries = {}
            for item in items:
                dev_id = item.get('device_id', 'unknown')
                if dev_id not in device_summaries:
                    device_summaries[dev_id] = {
                        'device_id': dev_id,
                        'total_metrics': 0,
                        'active_metrics': 0,
                        'latest_timestamp': None,
                        'metric_types': set()
                    }
                
                summary = device_summaries[dev_id]
                summary['total_metrics'] += 1
                
                if item.get('status') == MetricStatus.ACTIVE:
                    summary['active_metrics'] += 1
                
                timestamp = item.get('timestamp')
                if timestamp and (summary['latest_timestamp'] is None or timestamp > summary['latest_timestamp']):
                    summary['latest_timestamp'] = timestamp
                
                metric_name = item.get('metric_name')
                if metric_name:
                    summary['metric_types'].add(metric_name)
            
            # MetricSummaryオブジェクトに変換
            summaries = []
            for dev_id, summary_data in device_summaries.items():
                summary = MetricSummary(
                    device_id=dev_id,
                    total_metrics=summary_data['total_metrics'],
                    active_metrics=summary_data['active_metrics'],
                    latest_timestamp=summary_data['latest_timestamp'],
                    metric_types=list(summary_data['metric_types'])
                )
                summaries.append(summary)
            
            return summaries
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            raise
    
    async def get_metric(self, metric_id: str) -> Optional[MetricResponse]:
        """メトリクス詳細取得"""
        try:
            response = self.metrics_table.get_item(
                Key={'metric_id': metric_id}
            )
            
            if 'Item' in response:
                return MetricResponse(**response['Item'])
            return None
        except Exception as e:
            logger.error(f"Failed to get metric {metric_id}: {e}")
            raise
    
    async def create_metric(self, metric_data: MetricCreate) -> MetricResponse:
        """メトリクス作成"""
        try:
            metric_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            metric_item = {
                'metric_id': metric_id,
                'device_id': metric_data.device_id,
                'metric_name': metric_data.metric_name,
                'value': metric_data.value,
                'unit': metric_data.unit,
                'status': metric_data.status.value,
                'metadata': metric_data.metadata or {},
                'timestamp': now.isoformat(),
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            # DynamoDBに保存
            self.metrics_table.put_item(Item=metric_item)
            
            logger.info(f"Metric created successfully: {metric_id}")
            
            return MetricResponse(
                metric_id=metric_id,
                device_id=metric_data.device_id,
                metric_name=metric_data.metric_name,
                value=metric_data.value,
                unit=metric_data.unit,
                status=metric_data.status,
                metadata=metric_data.metadata,
                timestamp=now,
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            logger.error(f"Failed to create metric: {e}")
            raise
    
    async def update_metric(self, metric_id: str, metric_data: MetricUpdate) -> MetricResponse:
        """メトリクス更新"""
        try:
            now = datetime.now(timezone.utc)
            
            # 更新するフィールドを構築
            update_expression = "SET updated_at = :updated_at"
            expression_attribute_values = {':updated_at': now.isoformat()}
            
            if metric_data.value is not None:
                update_expression += ", #value = :value"
                expression_attribute_values[':value'] = metric_data.value
                expression_attribute_values['#value'] = 'value'
                
            if metric_data.unit is not None:
                update_expression += ", unit = :unit"
                expression_attribute_values[':unit'] = metric_data.unit
                
            if metric_data.status is not None:
                update_expression += ", #status = :status"
                expression_attribute_values[':status'] = metric_data.status.value
                expression_attribute_values['#status'] = 'status'
                
            if metric_data.metadata is not None:
                update_expression += ", metadata = :metadata"
                expression_attribute_values[':metadata'] = metric_data.metadata
            
            # DynamoDBを更新
            update_kwargs = {
                'Key': {'metric_id': metric_id},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            # ExpressionAttributeNamesが必要な場合
            if '#value' in expression_attribute_values or '#status' in expression_attribute_values:
                expression_attribute_names = {}
                if '#value' in expression_attribute_values:
                    expression_attribute_names['#value'] = 'value'
                if '#status' in expression_attribute_values:
                    expression_attribute_names['#status'] = 'status'
                update_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
            self.metrics_table.update_item(**update_kwargs)
            
            # 更新後のメトリクス情報を取得
            updated_metric = await self.get_metric(metric_id)
            if not updated_metric:
                raise ValueError(f"Metric {metric_id} not found after update")
                
            logger.info(f"Metric updated successfully: {metric_id}")
            return updated_metric
            
        except Exception as e:
            logger.error(f"Failed to update metric {metric_id}: {e}")
            raise
    
    async def delete_metric(self, metric_id: str) -> bool:
        """メトリクス削除"""
        try:
            # DynamoDBから削除
            self.metrics_table.delete_item(
                Key={'metric_id': metric_id}
            )
            
            logger.info(f"Metric deleted successfully: {metric_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete metric {metric_id}: {e}")
            raise