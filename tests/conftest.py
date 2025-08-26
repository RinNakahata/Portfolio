"""
Pytest Configuration and Fixtures
pytest設定とフィクスチャ
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

from app.services.user_service import UserService
from app.services.metric_service import MetricService
from app.models.user import UserCreate, UserUpdate
from app.models.metric import MetricCreate, MetricUpdate, MetricStatus


@pytest.fixture
def mock_users_table():
    """ユーザーテーブルのモック"""
    table = Mock()
    
    # サンプルユーザーデータ
    sample_users = [
        {
            'user_id': 'user-001',
            'username': 'testuser1',
            'email': 'test1@example.com',
            'full_name': 'Test User 1',
            'is_active': True,
            'created_at': '2024-01-01T00:00:00+00:00',
            'updated_at': '2024-01-01T00:00:00+00:00'
        },
        {
            'user_id': 'user-002',
            'username': 'testuser2',
            'email': 'test2@example.com',
            'full_name': 'Test User 2',
            'is_active': False,
            'created_at': '2024-01-02T00:00:00+00:00',
            'updated_at': '2024-01-02T00:00:00+00:00'
        }
    ]
    
    # scan操作のモック
    def mock_scan(**kwargs):
        limit = kwargs.get('Limit', 10)
        items = sample_users[:limit]
        return {
            'Items': items,
            'Count': len(items),
            'ScannedCount': len(items)
        }
    
    # get_item操作のモック
    def mock_get_item(**kwargs):
        user_id = kwargs.get('Key', {}).get('user_id')
        for user in sample_users:
            if user['user_id'] == user_id:
                return {'Item': user}
        return {}
    
    # query操作のモック（GSI用）
    def mock_query(**kwargs):
        index_name = kwargs.get('IndexName')
        if index_name == 'username-index':
            username = kwargs.get('ExpressionAttributeValues', {}).get(':username')
            for user in sample_users:
                if user['username'] == username:
                    return {'Items': [user]}
        elif index_name == 'email-index':
            email = kwargs.get('ExpressionAttributeValues', {}).get(':email')
            for user in sample_users:
                if user['email'] == email:
                    return {'Items': [user]}
        return {'Items': []}
    
    # put_item操作のモック
    def mock_put_item(**kwargs):
        return {}
    
    # update_item操作のモック
    def mock_update_item(**kwargs):
        return {'Attributes': sample_users[0]}
    
    # delete_item操作のモック
    def mock_delete_item(**kwargs):
        return {}
    
    table.scan = mock_scan
    table.get_item = mock_get_item
    table.query = mock_query
    table.put_item = mock_put_item
    table.update_item = mock_update_item
    table.delete_item = mock_delete_item
    
    return table


@pytest.fixture
def mock_metrics_table():
    """メトリクステーブルのモック"""
    table = Mock()
    
    # サンプルメトリクスデータ
    sample_metrics = [
        {
            'metric_id': 'metric-001',
            'device_id': 'device-001',
            'metric_name': 'temperature',
            'value': 25.5,
            'unit': 'celsius',
            'status': 'active',
            'metadata': {'location': 'room1'},
            'timestamp': '2024-01-01T12:00:00+00:00',
            'created_at': '2024-01-01T12:00:00+00:00',
            'updated_at': '2024-01-01T12:00:00+00:00'
        },
        {
            'metric_id': 'metric-002',
            'device_id': 'device-001',
            'metric_name': 'humidity',
            'value': 60.0,
            'unit': 'percent',
            'status': 'active',
            'metadata': {'location': 'room1'},
            'timestamp': '2024-01-01T12:00:00+00:00',
            'created_at': '2024-01-01T12:00:00+00:00',
            'updated_at': '2024-01-01T12:00:00+00:00'
        }
    ]
    
    # scan操作のモック
    def mock_scan(**kwargs):
        limit = kwargs.get('Limit', 10)
        items = sample_metrics[:limit]
        return {
            'Items': items,
            'Count': len(items),
            'ScannedCount': len(items)
        }
    
    # get_item操作のモック
    def mock_get_item(**kwargs):
        metric_id = kwargs.get('Key', {}).get('metric_id')
        for metric in sample_metrics:
            if metric['metric_id'] == metric_id:
                return {'Item': metric}
        return {}
    
    # query操作のモック（GSI用）
    def mock_query(**kwargs):
        index_name = kwargs.get('IndexName')
        if index_name == 'timestamp-index':
            device_id = kwargs.get('ExpressionAttributeValues', {}).get(':device_id')
            items = [m for m in sample_metrics if m['device_id'] == device_id]
            return {'Items': items}
        return {'Items': []}
    
    # put_item操作のモック
    def mock_put_item(**kwargs):
        return {}
    
    # update_item操作のモック
    def mock_update_item(**kwargs):
        return {'Attributes': sample_metrics[0]}
    
    # delete_item操作のモック
    def mock_delete_item(**kwargs):
        return {}
    
    table.scan = mock_scan
    table.get_item = mock_get_item
    table.query = mock_query
    table.put_item = mock_put_item
    table.update_item = mock_update_item
    table.delete_item = mock_delete_item
    
    return table


@pytest.fixture
def user_service(mock_users_table):
    """UserServiceのインスタンス"""
    return UserService(mock_users_table)


@pytest.fixture
def metric_service(mock_metrics_table):
    """MetricServiceのインスタンス"""
    return MetricService(mock_metrics_table)


@pytest.fixture
def sample_user_create():
    """サンプルユーザー作成データ"""
    return UserCreate(
        username='newuser',
        email='newuser@example.com',
        full_name='New User',
        is_active=True
    )


@pytest.fixture
def sample_user_update():
    """サンプルユーザー更新データ"""
    return UserUpdate(
        full_name='Updated User Name',
        is_active=False
    )


@pytest.fixture
def sample_metric_create():
    """サンプルメトリクス作成データ"""
    return MetricCreate(
        device_id='device-003',
        metric_name='pressure',
        value=1013.25,
        unit='hPa',
        status=MetricStatus.ACTIVE,
        metadata={'location': 'outdoor'}
    )


@pytest.fixture
def sample_metric_update():
    """サンプルメトリクス更新データ"""
    return MetricUpdate(
        value=1015.0,
        status=MetricStatus.INACTIVE
    )
