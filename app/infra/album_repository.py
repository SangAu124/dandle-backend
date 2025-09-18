from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from app.domain.album import Album, AlbumShare, album_photos


class AlbumRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, album_data: dict) -> Album:
        """새로운 앨범 생성"""
        album = Album(**album_data)
        self.db.add(album)
        self.db.commit()
        self.db.refresh(album)
        return album

    def get_by_id(self, album_id: int) -> Optional[Album]:
        """ID로 앨범 조회"""
        return (
            self.db.query(Album)
            .filter(and_(Album.id == album_id, Album.is_active == True))
            .first()
        )

    def get_albums(
        self,
        created_by_id: Optional[int] = None,
        group_id: Optional[int] = None,
        album_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Album]:
        """앨범 목록 조회"""
        query = self.db.query(Album).filter(Album.is_active == True)

        if created_by_id is not None:
            query = query.filter(Album.created_by_id == created_by_id)

        if group_id is not None:
            query = query.filter(Album.group_id == group_id)

        if album_type is not None:
            query = query.filter(Album.album_type == album_type)

        return (
            query
            .order_by(Album.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, album_id: int, update_data: dict) -> Optional[Album]:
        """앨범 정보 수정"""
        album = self.get_by_id(album_id)
        if not album:
            return None

        for key, value in update_data.items():
            if hasattr(album, key):
                setattr(album, key, value)

        self.db.commit()
        self.db.refresh(album)
        return album

    def delete(self, album_id: int) -> bool:
        """앨범 삭제 (소프트 삭제)"""
        album = self.get_by_id(album_id)
        if not album:
            return False

        album.is_active = False
        self.db.commit()
        return True

    def add_photo_to_album(self, album_id: int, photo_id: int) -> bool:
        """앨범에 사진 추가"""
        # 이미 추가되어 있는지 확인
        if self.is_photo_in_album(album_id, photo_id):
            return False

        # Many-to-Many 관계 테이블에 직접 삽입
        stmt = album_photos.insert().values(album_id=album_id, photo_id=photo_id)
        self.db.execute(stmt)
        self.db.commit()
        return True

    def remove_photo_from_album(self, album_id: int, photo_id: int) -> bool:
        """앨범에서 사진 제거"""
        stmt = album_photos.delete().where(
            and_(
                album_photos.c.album_id == album_id,
                album_photos.c.photo_id == photo_id
            )
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def is_photo_in_album(self, album_id: int, photo_id: int) -> bool:
        """사진이 앨범에 있는지 확인"""
        result = (
            self.db.query(album_photos)
            .filter(
                and_(
                    album_photos.c.album_id == album_id,
                    album_photos.c.photo_id == photo_id
                )
            )
            .first()
        )
        return result is not None

    def get_album_photos(self, album_id: int, skip: int = 0, limit: int = 50):
        """앨범의 사진 목록 조회"""
        from app.domain.photo import Photo

        return (
            self.db.query(Photo)
            .join(album_photos)
            .filter(
                and_(
                    album_photos.c.album_id == album_id,
                    Photo.is_active == True
                )
            )
            .order_by(album_photos.c.added_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_album_photo_count(self, album_id: int) -> int:
        """앨범의 사진 개수 조회"""
        from app.domain.photo import Photo

        return (
            self.db.query(func.count(Photo.id))
            .join(album_photos)
            .filter(
                and_(
                    album_photos.c.album_id == album_id,
                    Photo.is_active == True
                )
            )
            .scalar()
        )

    def create_album_share(self, share_data: dict) -> AlbumShare:
        """앨범 공유 생성"""
        share = AlbumShare(**share_data)
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    def get_album_share(self, album_id: int, shared_with_id: int) -> Optional[AlbumShare]:
        """특정 사용자와의 앨범 공유 조회"""
        return (
            self.db.query(AlbumShare)
            .filter(
                and_(
                    AlbumShare.album_id == album_id,
                    AlbumShare.shared_with_id == shared_with_id,
                    AlbumShare.is_active == True
                )
            )
            .first()
        )

    def get_album_shares(self, album_id: int) -> List[AlbumShare]:
        """앨범의 모든 공유 목록 조회"""
        return (
            self.db.query(AlbumShare)
            .filter(
                and_(
                    AlbumShare.album_id == album_id,
                    AlbumShare.is_active == True
                )
            )
            .all()
        )

    def get_shared_albums(self, user_id: int) -> List[AlbumShare]:
        """사용자가 공유받은 앨범 목록 조회"""
        return (
            self.db.query(AlbumShare)
            .options(joinedload(AlbumShare.album))
            .filter(
                and_(
                    AlbumShare.shared_with_id == user_id,
                    AlbumShare.is_active == True
                )
            )
            .all()
        )

    def update_album_share(self, share_id: int, update_data: dict) -> Optional[AlbumShare]:
        """앨범 공유 정보 수정"""
        share = self.db.query(AlbumShare).filter(AlbumShare.id == share_id).first()
        if not share:
            return None

        for key, value in update_data.items():
            if hasattr(share, key):
                setattr(share, key, value)

        self.db.commit()
        self.db.refresh(share)
        return share

    def get_public_albums(self, skip: int = 0, limit: int = 50) -> List[Album]:
        """공개 앨범 목록 조회"""
        return (
            self.db.query(Album)
            .filter(
                and_(
                    Album.is_active == True,
                    Album.is_public == True
                )
            )
            .order_by(Album.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )