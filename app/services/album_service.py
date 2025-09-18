from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.album import Album, AlbumShare
from app.infra.album_repository import AlbumRepository


class AlbumService:
    def __init__(self, db: Session):
        self.repository = AlbumRepository(db)

    def create_album(
        self,
        name: str,
        created_by_id: int,
        album_type: str,
        description: Optional[str] = None,
        group_id: Optional[int] = None,
        is_public: bool = False,
        auto_criteria: Optional[str] = None
    ) -> Album:
        """새로운 앨범 생성"""
        album_data = {
            "name": name,
            "description": description,
            "album_type": album_type,
            "auto_criteria": auto_criteria,
            "is_public": is_public,
            "created_by_id": created_by_id,
            "group_id": group_id,
            "is_active": True
        }

        return self.repository.create(album_data)

    def create_auto_album(
        self,
        name: str,
        created_by_id: int,
        criteria: str,
        group_id: Optional[int] = None
    ) -> Album:
        """자동 앨범 생성 (얼굴 인식, 날짜, 위치 기반)"""
        return self.create_album(
            name=name,
            created_by_id=created_by_id,
            album_type="auto",
            auto_criteria=criteria,
            group_id=group_id,
            is_public=False
        )

    def get_album_by_id(self, album_id: int) -> Optional[Album]:
        """ID로 앨범 조회"""
        return self.repository.get_by_id(album_id)

    def get_albums(
        self,
        created_by_id: Optional[int] = None,
        group_id: Optional[int] = None,
        album_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Album]:
        """앨범 목록 조회"""
        return self.repository.get_albums(
            created_by_id=created_by_id,
            group_id=group_id,
            album_type=album_type,
            skip=skip,
            limit=limit
        )

    def get_user_albums(self, user_id: int) -> List[Album]:
        """사용자의 모든 앨범 조회 (생성한 앨범 + 공유받은 앨범)"""
        created_albums = self.repository.get_albums(created_by_id=user_id)
        shared_albums = self.repository.get_shared_albums(user_id)

        # 중복 제거
        all_albums = created_albums + [share.album for share in shared_albums]
        unique_albums = {album.id: album for album in all_albums}

        return list(unique_albums.values())

    def update_album(self, album_id: int, update_data: dict) -> Optional[Album]:
        """앨범 정보 수정"""
        return self.repository.update(album_id, update_data)

    def delete_album(self, album_id: int) -> bool:
        """앨범 삭제 (소프트 삭제)"""
        return self.repository.delete(album_id)

    def add_photos_to_album(self, album_id: int, photo_ids: List[int]) -> bool:
        """앨범에 사진들 추가"""
        album = self.repository.get_by_id(album_id)
        if not album:
            return False

        for photo_id in photo_ids:
            if not self.repository.is_photo_in_album(album_id, photo_id):
                self.repository.add_photo_to_album(album_id, photo_id)

        return True

    def remove_photo_from_album(self, album_id: int, photo_id: int) -> bool:
        """앨범에서 사진 제거"""
        return self.repository.remove_photo_from_album(album_id, photo_id)

    def get_album_photos(self, album_id: int, skip: int = 0, limit: int = 50):
        """앨범의 사진 목록 조회"""
        return self.repository.get_album_photos(album_id, skip, limit)

    def set_cover_photo(self, album_id: int, photo_id: int) -> bool:
        """앨범 커버 사진 설정"""
        # 사진이 앨범에 있는지 확인
        if not self.repository.is_photo_in_album(album_id, photo_id):
            return False

        return self.repository.update(album_id, {"cover_photo_id": photo_id}) is not None

    def share_album(
        self,
        album_id: int,
        shared_with_id: int,
        permission: str = "view"
    ) -> Optional[AlbumShare]:
        """앨범 공유"""
        # 이미 공유되어 있는지 확인
        existing_share = self.repository.get_album_share(album_id, shared_with_id)
        if existing_share:
            # 기존 공유 설정 업데이트
            return self.repository.update_album_share(existing_share.id, {"permission": permission})

        # 새로운 공유 생성
        share_data = {
            "album_id": album_id,
            "shared_with_id": shared_with_id,
            "permission": permission,
            "is_active": True
        }

        return self.repository.create_album_share(share_data)

    def revoke_album_share(self, album_id: int, shared_with_id: int) -> bool:
        """앨범 공유 취소"""
        share = self.repository.get_album_share(album_id, shared_with_id)
        if not share:
            return False

        return self.repository.update_album_share(share.id, {"is_active": False}) is not None

    def get_album_shares(self, album_id: int) -> List[AlbumShare]:
        """앨범 공유 목록 조회"""
        return self.repository.get_album_shares(album_id)

    def auto_organize_photos_by_face(self, user_id: int, face_id: int) -> Album:
        """얼굴 인식 기반 자동 앨범 생성"""
        # TODO: 얼굴 인식 서비스와 연동하여 같은 얼굴이 포함된 사진들로 앨범 생성
        album_name = f"Person {face_id}"
        album = self.create_auto_album(
            name=album_name,
            created_by_id=user_id,
            criteria=f"face:{face_id}"
        )

        # TODO: 해당 얼굴이 포함된 사진들을 앨범에 추가
        # photos = face_service.get_photos_with_face(face_id)
        # self.add_photos_to_album(album.id, [p.id for p in photos])

        return album