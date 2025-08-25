"""
Users Router
ユーザー管理エンドポイント
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query
from botocore.exceptions import ClientError

from app.models.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.dependencies import get_users_table
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def get_users(
    limit: int = Query(default=10, ge=1, le=100, description="取得件数"),
    offset: int = Query(default=0, ge=0, description="オフセット"),
    users_table=Depends(get_users_table)
) -> UserListResponse:
    """
    ユーザー一覧取得
    
    Args:
        limit: 取得件数 (1-100)
        offset: オフセット
        
    Returns:
        ユーザー一覧
    """
    try:
        user_service = UserService(users_table)
        result = await user_service.get_users(limit=limit, offset=offset)
        return result
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=500,
            detail="ユーザー一覧の取得に失敗しました"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    users_table=Depends(get_users_table)
) -> UserResponse:
    """
    ユーザー詳細取得
    
    Args:
        user_id: ユーザーID
        
    Returns:
        ユーザー詳細情報
    """
    try:
        user_service = UserService(users_table)
        user = await user_service.get_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )
            
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="ユーザー情報の取得に失敗しました"
        )


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    users_table=Depends(get_users_table)
) -> UserResponse:
    """
    ユーザー作成
    
    Args:
        user_data: ユーザー作成データ
        
    Returns:
        作成されたユーザー情報
    """
    try:
        user_service = UserService(users_table)
        
        # ユーザー名の重複チェック
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="このユーザー名は既に使用されています"
            )
        
        # メールアドレスの重複チェック
        existing_email = await user_service.get_user_by_email(str(user_data.email))
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="このメールアドレスは既に使用されています"
            )
        
        # ユーザー作成
        new_user = await user_service.create_user(user_data)
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=500,
            detail="ユーザーの作成に失敗しました"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    users_table=Depends(get_users_table)
) -> UserResponse:
    """
    ユーザー情報更新
    
    Args:
        user_id: ユーザーID
        user_data: 更新データ
        
    Returns:
        更新されたユーザー情報
    """
    try:
        user_service = UserService(users_table)
        
        # ユーザー存在確認
        existing_user = await user_service.get_user(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )
        
        # 更新実行
        updated_user = await user_service.update_user(user_id, user_data)
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="ユーザー情報の更新に失敗しました"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    users_table=Depends(get_users_table)
) -> dict:
    """
    ユーザー削除
    
    Args:
        user_id: ユーザーID
        
    Returns:
        削除結果
    """
    try:
        user_service = UserService(users_table)
        
        # ユーザー存在確認
        existing_user = await user_service.get_user(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )
        
        # 削除実行
        await user_service.delete_user(user_id)
        
        return {
            "message": "ユーザーを削除しました",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="ユーザーの削除に失敗しました"
        )