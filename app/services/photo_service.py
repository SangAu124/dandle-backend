from typing import Optional, List, BinaryIO
import hashlib
import uuid
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from sqlalchemy.orm import Session
from app.domain.photo import Photo, PhotoTag
from app.infra.photo_repository import PhotoRepository


class PhotoService:
    def __init__(self, db: Session, s3_client=None):
        self.repository = PhotoRepository(db)
        self.s3_client = s3_client  # AWS S3 클라이언트

    def upload_photo(
        self,
        file: BinaryIO,
        filename: str,
        uploaded_by_id: int,
        group_id: Optional[int] = None,
        bucket_name: str = "dandle-photos"
    ) -> Photo:
        """사진 업로드 처리"""
        # 1. 파일 해시 계산 (중복 방지)
        file_content = file.read()
        file_hash = self._calculate_file_hash(file_content)
        file.seek(0)  # 파일 포인터 리셋

        # 2. 중복 사진 검사
        existing_photo = self.repository.get_by_hash(file_hash)
        if existing_photo:
            raise ValueError("Photo already exists")

        # 3. 이미지 메타데이터 추출
        try:
            image = Image.open(file)
            width, height = image.size
            format_type = image.format
            exif_data = self._extract_exif_data(image)
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        # 4. S3 업로드
        s3_key = self._generate_s3_key(filename, uploaded_by_id)
        s3_url = self._upload_to_s3(file_content, bucket_name, s3_key)

        # 5. DB에 사진 정보 저장
        photo_data = {
            "filename": f"{uuid.uuid4()}_{filename}",
            "original_filename": filename,
            "file_path": s3_url,
            "file_size": len(file_content),
            "width": width,
            "height": height,
            "format": format_type,
            "s3_bucket": bucket_name,
            "s3_key": s3_key,
            "s3_url": s3_url,
            "uploaded_by_id": uploaded_by_id,
            "group_id": group_id,
            "file_hash": file_hash,
            "is_processed": False,
            "is_active": True,
            **exif_data
        }

        photo = self.repository.create(photo_data)

        # 6. 얼굴 인식 처리 큐에 추가 (비동기)
        # TODO: Celery 또는 다른 작업 큐 시스템 연동
        # self._queue_face_recognition(photo.id)

        return photo

    def get_photo_by_id(self, photo_id: int) -> Optional[Photo]:
        """ID로 사진 조회"""
        return self.repository.get_by_id(photo_id)

    def get_photos(
        self,
        group_id: Optional[int] = None,
        uploaded_by_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Photo]:
        """사진 목록 조회"""
        return self.repository.get_photos(
            group_id=group_id,
            uploaded_by_id=uploaded_by_id,
            skip=skip,
            limit=limit
        )

    def update_photo(self, photo_id: int, update_data: dict) -> Optional[Photo]:
        """사진 정보 수정"""
        return self.repository.update(photo_id, update_data)

    def delete_photo(self, photo_id: int) -> bool:
        """사진 삭제 (소프트 삭제)"""
        return self.repository.delete(photo_id)

    def add_photo_tag(self, photo_id: int, tag_name: str, confidence: float = 1.0) -> PhotoTag:
        """사진에 태그 추가"""
        tag_data = {
            "photo_id": photo_id,
            "tag_name": tag_name,
            "confidence": confidence
        }
        return self.repository.create_tag(tag_data)

    def get_photo_tags(self, photo_id: int) -> List[PhotoTag]:
        """사진 태그 조회"""
        return self.repository.get_photo_tags(photo_id)

    def mark_as_processed(self, photo_id: int) -> bool:
        """사진을 처리 완료로 표시"""
        return self.repository.update(photo_id, {"is_processed": True}) is not None

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """파일 해시 계산"""
        return hashlib.sha256(file_content).hexdigest()

    def _extract_exif_data(self, image: Image.Image) -> dict:
        """EXIF 데이터 추출"""
        exif_data = {}
        try:
            exif = image._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTime":
                        try:
                            exif_data["taken_at"] = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        except:
                            pass
                    elif tag == "Make":
                        exif_data["camera_make"] = value
                    elif tag == "Model":
                        exif_data["camera_model"] = value
                    # GPS 정보 추출 로직 추가 가능
        except:
            pass
        return exif_data

    def _generate_s3_key(self, filename: str, user_id: int) -> str:
        """S3 키 생성"""
        timestamp = datetime.now().strftime("%Y/%m/%d")
        unique_id = str(uuid.uuid4())
        return f"photos/{user_id}/{timestamp}/{unique_id}_{filename}"

    def _upload_to_s3(self, file_content: bytes, bucket: str, key: str) -> str:
        """S3에 파일 업로드"""
        # TODO: 실제 S3 업로드 구현
        # self.s3_client.put_object(Bucket=bucket, Key=key, Body=file_content)
        return f"https://{bucket}.s3.amazonaws.com/{key}"