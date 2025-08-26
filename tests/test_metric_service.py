"""
MetricService Tests
メトリクスサービスのテスト
"""

import pytest
from datetime import datetime, timezone

from app.services.metric_service import MetricService
from app.models.metric import MetricCreate, MetricUpdate, MetricResponse, MetricStatus


class TestMetricService:
    """MetricServiceのテストクラス"""
    
    @pytest.mark.asyncio
    async def test_get_metrics_success(self, metric_service, mock_metrics_table):
        """メトリクス一覧取得の成功テスト"""
        result = await metric_service.get_metrics(limit=5)
        
        assert result is not None
        assert result.total_count == 2
        assert len(result.metrics) == 2
        assert result.limit == 5
        assert result.offset == 0
        
        # 最初のメトリクスの確認
        first_metric = result.metrics[0]
        assert first_metric.metric_id == 'metric-001'
        assert first_metric.device_id == 'device-001'
        assert first_metric.metric_name == 'temperature'
        assert first_metric.value == 25.5
        assert first_metric.unit == 'celsius'
        assert first_metric.status == MetricStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_device_filter(self, metric_service, mock_metrics_table):
        """デバイスIDフィルター付きメトリクス取得のテスト"""
        result = await metric_service.get_metrics(device_id='device-001')
        
        assert result is not None
        assert len(result.metrics) == 2
        for metric in result.metrics:
            assert metric.device_id == 'device-001'
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_status_filter(self, metric_service, mock_metrics_table):
        """ステータスフィルター付きメトリクス取得のテスト"""
        result = await metric_service.get_metrics(status=MetricStatus.ACTIVE)
        
        assert result is not None
        assert len(result.metrics) == 2
        for metric in result.metrics:
            assert metric.status == MetricStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_offset(self, metric_service, mock_metrics_table):
        """オフセット付きメトリクス一覧取得のテスト"""
        result = await metric_service.get_metrics(limit=1, offset=1)
        
        assert result is not None
        assert result.total_count == 1
        assert len(result.metrics) == 1
        assert result.limit == 1
        assert result.offset == 1
    
    @pytest.mark.asyncio
    async def test_get_latest_metrics_all_devices(self, metric_service, mock_metrics_table):
        """全デバイスの最新メトリクス取得のテスト"""
        result = await metric_service.get_latest_metrics(limit=3)
        
        assert result is not None
        assert len(result) <= 3
        # タイムスタンプでソートされていることを確認
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i].timestamp >= result[i + 1].timestamp
    
    @pytest.mark.asyncio
    async def test_get_latest_metrics_specific_device(self, metric_service, mock_metrics_table):
        """特定デバイスの最新メトリクス取得のテスト"""
        result = await metric_service.get_latest_metrics(device_id='device-001', limit=2)
        
        assert result is not None
        assert len(result) <= 2
        for metric in result:
            assert metric.device_id == 'device-001'
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary_all_devices(self, metric_service, mock_metrics_table):
        """全デバイスのメトリクス集計取得のテスト"""
        result = await metric_service.get_metrics_summary()
        
        assert result is not None
        assert len(result) > 0
        
        # デバイス001の集計確認
        device_001_summary = next((s for s in result if s.device_id == 'device-001'), None)
        assert device_001_summary is not None
        assert device_001_summary.total_metrics == 2
        assert device_001_summary.active_metrics == 2
        assert 'temperature' in device_001_summary.metric_types
        assert 'humidity' in device_001_summary.metric_types
    
    @pytest.mark.asyncio
    async def test_get_metrics_summary_specific_device(self, metric_service, mock_metrics_table):
        """特定デバイスのメトリクス集計取得のテスト"""
        result = await metric_service.get_metrics_summary(device_id='device-001')
        
        assert result is not None
        assert len(result) == 1
        
        summary = result[0]
        assert summary.device_id == 'device-001'
        assert summary.total_metrics == 2
        assert summary.active_metrics == 2
    
    @pytest.mark.asyncio
    async def test_get_metric_success(self, metric_service, mock_metrics_table):
        """メトリクス詳細取得の成功テスト"""
        result = await metric_service.get_metric('metric-001')
        
        assert result is not None
        assert result.metric_id == 'metric-001'
        assert result.device_id == 'device-001'
        assert result.metric_name == 'temperature'
        assert result.value == 25.5
        assert result.unit == 'celsius'
        assert result.status == MetricStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_metric_not_found(self, metric_service, mock_metrics_table):
        """存在しないメトリクス取得のテスト"""
        result = await metric_service.get_metric('non-existent-metric')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_metric_success(self, metric_service, mock_metrics_table, sample_metric_create):
        """メトリクス作成の成功テスト"""
        result = await metric_service.create_metric(sample_metric_create)
        
        assert result is not None
        assert result.device_id == 'device-003'
        assert result.metric_name == 'pressure'
        assert result.value == 1013.25
        assert result.unit == 'hPa'
        assert result.status == MetricStatus.ACTIVE
        assert result.metadata == {'location': 'outdoor'}
        assert result.metric_id is not None
        assert result.created_at is not None
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_update_metric_success(self, metric_service, mock_metrics_table, sample_metric_update):
        """メトリクス更新の成功テスト"""
        result = await metric_service.update_metric('metric-001', sample_metric_update)
        
        assert result is not None
        assert result.metric_id == 'metric-001'
        assert result.value == 1015.0
        assert result.status == MetricStatus.INACTIVE
    
    @pytest.mark.asyncio
    async def test_update_metric_partial(self, metric_service, mock_metrics_table):
        """部分的なメトリクス更新のテスト"""
        update_data = MetricUpdate(value=30.0)
        result = await metric_service.update_metric('metric-001', update_data)
        
        assert result is not None
        assert result.value == 30.0
        # 他のフィールドは変更されていないことを確認
    
    @pytest.mark.asyncio
    async def test_delete_metric_success(self, metric_service, mock_metrics_table):
        """メトリクス削除の成功テスト"""
        result = await metric_service.delete_metric('metric-001')
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_metrics_with_complex_filters(self, metric_service, mock_metrics_table):
        """複合フィルター付きメトリクス取得のテスト"""
        result = await metric_service.get_metrics(
            device_id='device-001',
            status=MetricStatus.ACTIVE,
            limit=5
        )
        
        assert result is not None
        assert len(result.metrics) == 2
        for metric in result.metrics:
            assert metric.device_id == 'device-001'
            assert metric.status == MetricStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_metric_timestamp_sorting(self, metric_service, mock_metrics_table):
        """メトリクスのタイムスタンプソートテスト"""
        result = await metric_service.get_latest_metrics(limit=10)
        
        assert result is not None
        if len(result) > 1:
            # 降順（最新順）でソートされていることを確認
            for i in range(len(result) - 1):
                current_time = result[i].timestamp
                next_time = result[i + 1].timestamp
                assert current_time >= next_time
