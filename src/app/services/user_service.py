"""
User Service
ユーザー管理ビジネスロジック
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import uuid
import hashlib

from app.models.user import UserCreate, UserUpdate, UserResponse, UserListResponse

logger = logging.getLogger(__name__)


class UserService:
    """ユーザー管理サービス"""
    
    def __init__(self, users_table):
        self.users_table = users_table
    
    async def get_users(self, limit: int = 10, offset: int = 0) -> UserListResponse:
        """ユーザー一覧取得"""
        try:
            # DynamoDBのscan操作でユーザー一覧取得
            scan_kwargs = {
                'Limit': limit
            }
            
            # offsetがある場合はExclusiveStartKeyを設定
            if offset and offset > 0:
                # 簡易的なoffset実装（実際のプロダクションではより効率的な方法を使用）
                response = self.users_table.scan()
                items = response.get('Items', [])
                if offset < len(items):
                    items = items[offset:offset + limit]
                else:
                    items = []
                count = len(items)
            else:
                response = self.users_table.scan(**scan_kwargs)
                items = response.get('Items', [])
                count = response.get('Count', 0)
            
            users = [UserResponse(**item) for item in items]
            return UserListResponse(
                users=users,
                total_count=count,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """ユーザー詳細取得"""
        try:
            response = self.users_table.get_item(
                Key={'user_id': user_id}
            )
            
            if 'Item' in response:
                return UserResponse(**response['Item'])
            return None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """ユーザー名でユーザー取得"""
        try:
            # GSI(username-index)を使用して取得
            response = self.users_table.query(
                IndexName='username-index',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            items = response.get('Items', [])
            if items:
                return UserResponse(**items[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """メールアドレスでユーザー取得"""
        try:
            # GSI(email-index)を使用して取得
            response = self.users_table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            items = response.get('Items', [])
            if items:
                return UserResponse(**items[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """ユーザー作成"""
        try:
            user_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # パスワードハッシュ化（実際のプロダクションではbcrypt等を使用）
            hashed_password = self._hash_password(user_data.password) if hasattr(user_data, 'password') else None
            
            user_item = {
                'user_id': user_id,
                'username': user_data.username,
                'email': user_data.email,
                'full_name': user_data.full_name,
                'is_active': user_data.is_active,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            if hashed_password:
                user_item['hashed_password'] = hashed_password
            
            # DynamoDBに保存
            self.users_table.put_item(Item=user_item)
            
            logger.info(f"User created successfully: {user_id}")
            
            return UserResponse(
                user_id=user_id,
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                is_active=user_data.is_active,
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """ユーザー更新"""
        try:
            now = datetime.now(timezone.utc)
            
            # 更新するフィールドを構築
            update_expression = "SET updated_at = :updated_at"
            expression_attribute_values = {':updated_at': now.isoformat()}
            
            if user_data.username is not None:
                update_expression += ", username = :username"
                expression_attribute_values[':username'] = user_data.username
                
            if user_data.email is not None:
                update_expression += ", email = :email"
                expression_attribute_values[':email'] = user_data.email
                
            if user_data.full_name is not None:
                update_expression += ", full_name = :full_name"
                expression_attribute_values[':full_name'] = user_data.full_name
                
            if user_data.is_active is not None:
                update_expression += ", is_active = :is_active"
                expression_attribute_values[':is_active'] = user_data.is_active
            
            # DynamoDBを更新
            self.users_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            # 更新後のユーザー情報を取得
            updated_user = await self.get_user(user_id)
            if not updated_user:
                raise ValueError(f"User {user_id} not found after update")
                
            logger.info(f"User updated successfully: {user_id}")
            return updated_user
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """ユーザー削除"""
        try:
            # DynamoDBから削除
            self.users_table.delete_item(
                Key={'user_id': user_id}
            )
            
            logger.info(f"User deleted successfully: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
    
    def _hash_password(self, password: str) -> str:
        """パスワードハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()