from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    profile_image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """사용자 생성"""
    # TODO: UserService를 통한 사용자 생성 로직 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation not implemented yet"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """현재 로그인된 사용자 정보 조회"""
    # TODO: JWT 토큰을 통한 현재 사용자 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get current user not implemented yet"
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """특정 사용자 정보 조회"""
    # TODO: UserService를 통한 사용자 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user not implemented yet"
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    """사용자 정보 수정"""
    # TODO: UserService를 통한 사용자 정보 수정
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update user not implemented yet"
    )