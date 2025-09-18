from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.domain.photo import Photo, PhotoTag


class PhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, photo_data: dict) -> Photo:
        """새로운 사진 생성"""
        photo = Photo(**photo_data)
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def get_by_id(self, photo_id: int) -> Optional[Photo]:
        """ID로 사진 조회"""
        return (
            self.db.query(Photo)
            .filter(and_(Photo.id == photo_id, Photo.is_active == True))
            .first()
        )

    def get_by_hash(self, file_hash: str) -> Optional[Photo]:
        """파일 해시로 사진 조회"""
        return (
            self.db.query(Photo)
            .filter(and_(Photo.file_hash == file_hash, Photo.is_active == True))
            .first()
        )

    def get_photos(
        self,
        group_id: Optional[int] = None,
        uploaded_by_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Photo]:
        """사진 목록 조회"""
        query = self.db.query(Photo).filter(Photo.is_active == True)

        if group_id is not None:
            query = query.filter(Photo.group_id == group_id)

        if uploaded_by_id is not None:
            query = query.filter(Photo.uploaded_by_id == uploaded_by_id)

        return (
            query
            .order_by(Photo.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_unprocessed_photos(self, limit: int = 10) -> List[Photo]:
        """처리되지 않은 사진 목록 조회"""
        return (
            self.db.query(Photo)
            .filter(
                and_(
                    Photo.is_active == True,
                    Photo.is_processed == False
                )
            )
            .order_by(Photo.created_at.asc())
            .limit(limit)
            .all()
        )

    def update(self, photo_id: int, update_data: dict) -> Optional[Photo]:
        """사진 정보 수정"""
        photo = self.get_by_id(photo_id)
        if not photo:
            return None

        for key, value in update_data.items():
            if hasattr(photo, key):
                setattr(photo, key, value)

        self.db.commit()
        self.db.refresh(photo)
        return photo

    def delete(self, photo_id: int) -> bool:
        """사진 삭제 (소프트 삭제)"""
        photo = self.get_by_id(photo_id)
        if not photo:
            return False

        photo.is_active = False
        self.db.commit()
        return True

    def create_tag(self, tag_data: dict) -> PhotoTag:
        """사진 태그 생성"""
        tag = PhotoTag(**tag_data)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def get_photo_tags(self, photo_id: int) -> List[PhotoTag]:
        """사진의 태그 목록 조회"""
        return (
            self.db.query(PhotoTag)
            .filter(PhotoTag.photo_id == photo_id)
            .order_by(PhotoTag.confidence.desc())
            .all()
        )

    def delete_photo_tag(self, tag_id: int) -> bool:
        """사진 태그 삭제"""
        tag = self.db.query(PhotoTag).filter(PhotoTag.id == tag_id).first()
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()
        return True

    def search_photos_by_tag(self, tag_name: str, limit: int = 50) -> List[Photo]:
        """태그로 사진 검색"""
        return (
            self.db.query(Photo)
            .join(PhotoTag)
            .filter(
                and_(
                    PhotoTag.tag_name.ilike(f"%{tag_name}%"),
                    Photo.is_active == True
                )
            )
            .order_by(PhotoTag.confidence.desc())
            .limit(limit)
            .all()
        )

    def get_photos_by_date_range(
        self,
        start_date,
        end_date,
        group_id: Optional[int] = None
    ) -> List[Photo]:
        """날짜 범위로 사진 조회"""
        query = (
            self.db.query(Photo)
            .filter(
                and_(
                    Photo.is_active == True,
                    Photo.taken_at >= start_date,
                    Photo.taken_at <= end_date
                )
            )
        )

        if group_id is not None:
            query = query.filter(Photo.group_id == group_id)

        return query.order_by(Photo.taken_at.desc()).all()