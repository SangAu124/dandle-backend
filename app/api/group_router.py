from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/groups", tags=["groups"])


# Pydantic schemas
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    group_type: str  # 'class', 'trip', 'event'
    is_public: bool = False
    max_members: int = 100


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    group_type: str
    invite_code: str
    is_active: bool
    is_public: bool
    max_members: int
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    max_members: Optional[int] = None


class GroupMembershipResponse(BaseModel):
    id: int
    group_id: int
    user_id: int
    role: str
    is_active: bool
    joined_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(group_data: GroupCreate):
    """그룹 생성"""
    # TODO: GroupService를 통한 그룹 생성
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Group creation not implemented yet"
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int):
    """그룹 정보 조회"""
    # TODO: GroupService를 통한 그룹 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get group not implemented yet"
    )


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(group_id: int, group_data: GroupUpdate):
    """그룹 정보 수정"""
    # TODO: GroupService를 통한 그룹 수정
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update group not implemented yet"
    )


@router.post("/{group_id}/join")
async def join_group(group_id: int):
    """그룹 가입"""
    # TODO: GroupService를 통한 그룹 가입
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Join group not implemented yet"
    )


@router.post("/join-by-code/{invite_code}")
async def join_group_by_code(invite_code: str):
    """초대 코드로 그룹 가입"""
    # TODO: GroupService를 통한 초대 코드 그룹 가입
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Join group by code not implemented yet"
    )


@router.get("/{group_id}/members", response_model=List[GroupMembershipResponse])
async def get_group_members(group_id: int):
    """그룹 멤버 목록 조회"""
    # TODO: GroupService를 통한 그룹 멤버 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get group members not implemented yet"
    )