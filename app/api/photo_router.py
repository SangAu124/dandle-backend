from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/photos", tags=["photos"])


# Pydantic schemas
class PhotoUpload(BaseModel):
    group_id: Optional[int] = None


class PhotoResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    width: Optional[int]
    height: Optional[int]
    format: Optional[str]
    s3_url: str
    uploaded_by_id: int
    group_id: Optional[int]
    is_processed: bool
    is_active: bool
    taken_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PhotoUpdate(BaseModel):
    group_id: Optional[int] = None


class PhotoTagResponse(BaseModel):
    id: int
    photo_id: int
    tag_name: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/upload", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    group_id: Optional[int] = Form(None)
):
    """사진 업로드"""
    # TODO: PhotoService를 통한 사진 업로드 처리
    # 1. 파일 검증 (이미지 형식, 크기 등)
    # 2. S3 업로드
    # 3. 메타데이터 추출
    # 4. DB 저장
    # 5. 얼굴 인식 작업 큐에 추가
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Photo upload not implemented yet"
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int):
    """사진 정보 조회"""
    # TODO: PhotoService를 통한 사진 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get photo not implemented yet"
    )


@router.get("/", response_model=List[PhotoResponse])
async def get_photos(
    group_id: Optional[int] = None,
    uploaded_by: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
):
    """사진 목록 조회"""
    # TODO: PhotoService를 통한 사진 목록 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get photos not implemented yet"
    )


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(photo_id: int, photo_data: PhotoUpdate):
    """사진 정보 수정"""
    # TODO: PhotoService를 통한 사진 정보 수정
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update photo not implemented yet"
    )


@router.delete("/{photo_id}")
async def delete_photo(photo_id: int):
    """사진 삭제"""
    # TODO: PhotoService를 통한 사진 삭제 (소프트 삭제)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete photo not implemented yet"
    )


@router.get("/{photo_id}/tags", response_model=List[PhotoTagResponse])
async def get_photo_tags(photo_id: int):
    """사진 태그 조회"""
    # TODO: PhotoService를 통한 사진 태그 조회
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get photo tags not implemented yet"
    )


@router.post("/{photo_id}/process")
async def process_photo(photo_id: int):
    """사진 얼굴 인식 처리 요청"""
    # TODO: PhotoService를 통한 얼굴 인식 처리 큐 추가
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Photo processing not implemented yet"
    )