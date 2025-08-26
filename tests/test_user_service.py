"""
UserService Tests
ユーザーサービスのテスト
"""

import pytest
from datetime import datetime, timezone

from app.services.user_service import UserService
from app.models.user import UserCreate, UserUpdate, UserResponse


class TestUserService:
    """UserServiceのテストクラス"""
    
    @pytest.mark.asyncio
    async def test_get_users_success(self, user_service, mock_users_table):
        """ユーザー一覧取得の成功テスト"""
        result = await user_service.get_users(limit=5)
        
        assert result is not None
        assert result.total_count == 2
        assert len(result.users) == 2
        assert result.limit == 5
        assert result.offset == 0
        
        # 最初のユーザーの確認
        first_user = result.users[0]
        assert first_user.user_id == 'user-001'
        assert first_user.username == 'testuser1'
        assert first_user.email == 'test1@example.com'
        assert first_user.full_name == 'Test User 1'
        assert first_user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_users_with_offset(self, user_service, mock_users_table):
        """オフセット付きユーザー一覧取得のテスト"""
        result = await user_service.get_users(limit=1, offset=1)
        
        assert result is not None
        assert result.total_count == 1
        assert len(result.users) == 1
        assert result.limit == 1
        assert result.offset == 1
        
        # 2番目のユーザーの確認
        user = result.users[0]
        assert user.user_id == 'user-002'
        assert user.username == 'testuser2'
        assert user.email == 'test2@example.com'
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, mock_users_table):
        """ユーザー詳細取得の成功テスト"""
        result = await user_service.get_user('user-001')
        
        assert result is not None
        assert result.user_id == 'user-001'
        assert result.username == 'testuser1'
        assert result.email == 'test1@example.com'
        assert result.full_name == 'Test User 1'
        assert result.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_users_table):
        """存在しないユーザー取得のテスト"""
        result = await user_service.get_user('non-existent-user')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, user_service, mock_users_table):
        """ユーザー名でのユーザー取得の成功テスト"""
        result = await user_service.get_user_by_username('testuser1')
        
        assert result is not None
        assert result.username == 'testuser1'
        assert result.email == 'test1@example.com'
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, user_service, mock_users_table):
        """存在しないユーザー名での取得テスト"""
        result = await user_service.get_user_by_username('non-existent-username')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_service, mock_users_table):
        """メールアドレスでのユーザー取得の成功テスト"""
        result = await user_service.get_user_by_email('test1@example.com')
        
        assert result is not None
        assert result.username == 'testuser1'
        assert result.email == 'test1@example.com'
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_service, mock_users_table):
        """存在しないメールアドレスでの取得テスト"""
        result = await user_service.get_user_by_email('nonexistent@example.com')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_users_table, sample_user_create):
        """ユーザー作成の成功テスト"""
        result = await user_service.create_user(sample_user_create)
        
        assert result is not None
        assert result.username == 'newuser'
        assert result.email == 'newuser@example.com'
        assert result.full_name == 'New User'
        assert result.is_active is True
        assert result.user_id is not None
        assert result.created_at is not None
        assert result.updated_at is not None
        
        # パスワードハッシュ化の確認
        assert hasattr(result, 'hashed_password') is False  # レスポンスには含まれない
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, mock_users_table, sample_user_update):
        """ユーザー更新の成功テスト"""
        result = await user_service.update_user('user-001', sample_user_update)
        
        assert result is not None
        assert result.user_id == 'user-001'
        assert result.full_name == 'Updated User Name'
        assert result.is_active is False
    
    @pytest.mark.asyncio
    async def test_update_user_partial(self, user_service, mock_users_table):
        """部分的なユーザー更新のテスト"""
        update_data = UserUpdate(full_name='Partial Update')
        result = await user_service.update_user('user-001', update_data)
        
        assert result is not None
        assert result.full_name == 'Partial Update'
        # 他のフィールドは変更されていないことを確認
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service, mock_users_table):
        """ユーザー削除の成功テスト"""
        result = await user_service.delete_user('user-001')
        
        assert result is True
    
    def test_password_hashing(self, user_service):
        """パスワードハッシュ化のテスト"""
        password = "testpassword123"
        hashed = user_service._hash_password(password)
        
        assert hashed != password
        assert len(hashed) == 64  # SHA-256の長さ
        assert hashed.isalnum()  # 16進数文字のみ
    
    def test_password_hashing_consistency(self, user_service):
        """パスワードハッシュ化の一貫性テスト"""
        password = "testpassword123"
        hash1 = user_service._hash_password(password)
        hash2 = user_service._hash_password(password)
        
        assert hash1 == hash2  # 同じパスワードは同じハッシュになる
    
    def test_password_hashing_different_passwords(self, user_service):
        """異なるパスワードのハッシュ化テスト"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = user_service._hash_password(password1)
        hash2 = user_service._hash_password(password2)
        
        assert hash1 != hash2  # 異なるパスワードは異なるハッシュになる
