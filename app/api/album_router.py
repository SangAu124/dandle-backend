from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/albums", tags=["albums"])


# Pydantic schemas
class AlbumCreate(BaseModel):
    name: str
    description: Optional[str] = None
    album_type: str  # 'personal', 'group', 'auto'
    group_id: Optional[int] = None
    is_public: bool = False


class AlbumResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    album_type: str
    auto_criteria: Optional[str]
    is_public: bool
    cover_photo_id: Optional[int]
    created_by_id: int
    group_id: Optional[int]
    is_active: bool
    photo_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class AlbumUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_photo_id: Optional[int] = None


class AlbumPhotoAdd(BaseModel):
    photo_ids: List[int]


class AlbumShareCreate(BaseModel):
    user_id: int
    permission: str = "view"  # 'view', 'edit', 'admin'


class AlbumShareResponse(BaseModel):
    id: int
    album_id: int
    shared_with_id: int
    permission: str
    is_active: bool
    shared_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(album_data: AlbumCreate):
    """앨범 생성"""
    # TODO: AlbumService를 통한 앨범 생성
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Album creation not implemented yet"
    )


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(album_id: int):
    """앨범 정보 조회"""
    # TODO: AlbumService를 통한 앨범 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get album not implemented yet"
    )


@router.get("/", response_model=List[AlbumResponse])
async def get_albums(
    album_type: Optional[str] = None,
    group_id: Optional[int] = None,
    created_by: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
):
    """앨범 목록 조회"""
    # TODO: AlbumService를 통한 앨범 목록 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get albums not implemented yet"
    )


@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(album_id: int, album_data: AlbumUpdate):
    """앨범 정보 수정"""
    # TODO: AlbumService를 통한 앨범 수정
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update album not implemented yet"
    )


@router.delete("/{album_id}")
async def delete_album(album_id: int):
    """앨범 삭제"""
    # TODO: AlbumService를 통한 앨범 삭제
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete album not implemented yet"
    )


@router.post("/{album_id}/photos")
async def add_photos_to_album(album_id: int, photo_data: AlbumPhotoAdd):
    """앨범에 사진 추가"""
    # TODO: AlbumService를 통한 앨범에 사진 추가
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Add photos to album not implemented yet"
    )


@router.delete("/{album_id}/photos/{photo_id}")
async def remove_photo_from_album(album_id: int, photo_id: int):
    """앨범에서 사진 제거"""
    # TODO: AlbumService를 통한 앨범에서 사진 제거
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Remove photo from album not implemented yet"
    )


@router.post("/{album_id}/share", response_model=AlbumShareResponse)
async def share_album(album_id: int, share_data: AlbumShareCreate):
    """앨범 공유"""
    # TODO: AlbumService를 통한 앨범 공유
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Share album not implemented yet"
    )


@router.get("/{album_id}/shares", response_model=List[AlbumShareResponse])
async def get_album_shares(album_id: int):
    """앨범 공유 목록 조회"""
    # TODO: AlbumService를 통한 앨범 공유 목록 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get album shares not implemented yet"
    )