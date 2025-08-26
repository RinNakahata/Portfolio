"""
API Integration Tests
API統合テスト
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.services.user_service import UserService
from app.services.metric_service import MetricService


class TestAPIIntegration:
    """API統合テストクラス"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_service(self):
        """UserServiceのモック"""
        return Mock(spec=UserService)
    
    @pytest.fixture
    def mock_metric_service(self):
        """MetricServiceのモック"""
        return Mock(spec=MetricService)
    
    def test_health_check(self, client):
        """ヘルスチェックエンドポイントのテスト"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_health_check_detailed(self, client):
        """詳細ヘルスチェックエンドポイントのテスト"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
    
    @patch('app.routers.users.get_user_service')
    def test_get_users_endpoint(self, mock_get_service, client, mock_user_service):
        """ユーザー一覧取得エンドポイントのテスト"""
        # モックサービスの設定
        mock_user_service.get_users.return_value = {
            "users": [
                {
                    "user_id": "user-001",
                    "username": "testuser1",
                    "email": "test1@example.com",
                    "full_name": "Test User 1",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00+00:00",
                    "updated_at": "2024-01-01T00:00:00+00:00"
                }
            ],
            "total_count": 1,
            "limit": 10,
            "offset": 0
        }
        mock_get_service.return_value = mock_user_service
        
        response = client.get("/users")
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) == 1
        assert data["users"][0]["username"] == "testuser1"
    
    @patch('app.routers.users.get_user_service')
    def test_get_user_by_id_endpoint(self, mock_get_service, client, mock_user_service):
        """ユーザー詳細取得エンドポイントのテスト"""
        # モックサービスの設定
        mock_user_service.get_user.return_value = {
            "user_id": "user-001",
            "username": "testuser1",
            "email": "test1@example.com",
            "full_name": "Test User 1",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00"
        }
        mock_get_service.return_value = mock_user_service
        
        response = client.get("/users/user-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user-001"
        assert data["username"] == "testuser1"
    
    @patch('app.routers.users.get_user_service')
    def test_create_user_endpoint(self, mock_get_service, client, mock_user_service):
        """ユーザー作成エンドポイントのテスト"""
        # モックサービスの設定
        mock_user_service.create_user.return_value = {
            "user_id": "user-003",
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "is_active": True,
            "created_at": "2024-01-03T00:00:00+00:00",
            "updated_at": "2024-01-03T00:00:00+00:00"
        }
        mock_get_service.return_value = mock_user_service
        
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "is_active": True
        }
        
        response = client.post("/users", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
    
    @patch('app.routers.metrics.get_metric_service')
    def test_get_metrics_endpoint(self, mock_get_service, client, mock_metric_service):
        """メトリクス一覧取得エンドポイントのテスト"""
        # モックサービスの設定
        mock_metric_service.get_metrics.return_value = {
            "metrics": [
                {
                    "metric_id": "metric-001",
                    "device_id": "device-001",
                    "metric_name": "temperature",
                    "value": 25.5,
                    "unit": "celsius",
                    "status": "active",
                    "metadata": {"location": "room1"},
                    "timestamp": "2024-01-01T12:00:00+00:00",
                    "created_at": "2024-01-01T12:00:00+00:00",
                    "updated_at": "2024-01-01T12:00:00+00:00"
                }
            ],
            "total_count": 1,
            "limit": 10,
            "offset": 0
        }
        mock_get_service.return_value = mock_metric_service
        
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert len(data["metrics"]) == 1
        assert data["metrics"][0]["metric_name"] == "temperature"
    
    @patch('app.routers.metrics.get_metric_service')
    def test_get_metrics_with_filters(self, mock_get_service, client, mock_metric_service):
        """フィルター付きメトリクス取得エンドポイントのテスト"""
        # モックサービスの設定
        mock_metric_service.get_metrics.return_value = {
            "metrics": [],
            "total_count": 0,
            "limit": 10,
            "offset": 0
        }
        mock_get_service.return_value = mock_metric_service
        
        response = client.get("/metrics?device_id=device-001&status=active")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
    
    @patch('app.routers.metrics.get_metric_service')
    def test_create_metric_endpoint(self, mock_get_service, client, mock_metric_service):
        """メトリクス作成エンドポイントのテスト"""
        # モックサービスの設定
        mock_metric_service.create_metric.return_value = {
            "metric_id": "metric-003",
            "device_id": "device-003",
            "metric_name": "pressure",
            "value": 1013.25,
            "unit": "hPa",
            "status": "active",
            "metadata": {"location": "outdoor"},
            "timestamp": "2024-01-03T12:00:00+00:00",
            "created_at": "2024-01-03T12:00:00+00:00",
            "updated_at": "2024-01-03T12:00:00+00:00"
        }
        mock_get_service.return_value = mock_metric_service
        
        metric_data = {
            "device_id": "device-003",
            "metric_name": "pressure",
            "value": 1013.25,
            "unit": "hPa",
            "status": "active",
            "metadata": {"location": "outdoor"}
        }
        
        response = client.post("/metrics", json=metric_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["metric_name"] == "pressure"
        assert data["device_id"] == "device-003"
    
    def test_invalid_user_data_validation(self, client):
        """無効なユーザーデータのバリデーションテスト"""
        invalid_user_data = {
            "username": "",  # 空文字列は無効
            "email": "invalid-email",  # 無効なメール形式
            "full_name": "Test User"
        }
        
        response = client.post("/users", json=invalid_user_data)
        
        assert response.status_code == 422  # バリデーションエラー
    
    def test_invalid_metric_data_validation(self, client):
        """無効なメトリクスデータのバリデーションテスト"""
        invalid_metric_data = {
            "device_id": "",  # 空文字列は無効
            "metric_name": "temp",
            "value": "invalid-value",  # 数値でない
            "unit": "celsius"
        }
        
        response = client.post("/metrics", json=invalid_metric_data)
        
        assert response.status_code == 422  # バリデーションエラー
    
    def test_not_found_endpoint(self, client):
        """存在しないエンドポイントのテスト"""
        response = client.get("/non-existent-endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """許可されていないHTTPメソッドのテスト"""
        response = client.put("/health")
        
        assert response.status_code == 405  # Method Not Allowed
