"""
User Data Models
ユーザーデータモデル
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """ユーザー基本モデル"""
    username: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")
    full_name: Optional[str] = Field(None, max_length=100, description="フルネーム")
    is_active: bool = Field(True, description="アクティブ状態")


class UserCreate(UserBase):
    """ユーザー作成用モデル"""
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")


class UserUpdate(BaseModel):
    """ユーザー更新用モデル"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """ユーザーレスポンス用モデル"""
    user_id: str = Field(..., description="ユーザーID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス用モデル"""
    users: list[UserResponse]
    total_count: int
    limit: int
    offset: int
    
    class Config:
        from_attributes = True