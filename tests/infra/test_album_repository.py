import pytest
from sqlalchemy.orm import Session
from app.infra.album_repository import AlbumRepository
from app.domain.user import User
from app.domain.group import Group
from app.domain.photo import Photo


class TestAlbumRepository:
    """AlbumRepository 테스트"""

    @pytest.fixture
    def repo(self, db_session: Session):
        """Repository fixture"""
        return AlbumRepository(db_session)

    @pytest.fixture
    def test_user(self, db_session: Session):
        """Test user fixture"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def test_group(self, db_session: Session, test_user):
        """Test group fixture"""
        group = Group(
            name="Test Group",
            description="Test Description",
            created_by_id=test_user.id
        )
        db_session.add(group)
        db_session.commit()
        db_session.refresh(group)
        return group

    @pytest.fixture
    def test_photo(self, db_session: Session, test_user):
        """Test photo fixture"""
        photo = Photo(
            filename="test.jpg",
            file_path="/test/path",
            file_size=1024,
            width=800,
            height=600,
            uploaded_by_id=test_user.id
        )
        db_session.add(photo)
        db_session.commit()
        db_session.refresh(photo)
        return photo

    def test_create(self, repo: AlbumRepository, test_user: User):
        """앨범 생성 테스트"""
        album_data = {
            "name": "Test Album",
            "description": "Test Description",
            "album_type": "personal",
            "created_by_id": test_user.id
        }

        album = repo.create(album_data)

        assert album.id is not None
        assert album.name == "Test Album"
        assert album.description == "Test Description"
        assert album.album_type == "personal"
        assert album.created_by_id == test_user.id
        assert album.is_active is True
        assert album.is_public is False

    def test_get_by_id_existing(self, repo: AlbumRepository, test_user: User):
        """ID로 기존 앨범 조회 테스트"""
        # 앨범 생성
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # ID로 조회
        found_album = repo.get_by_id(album.id)

        assert found_album is not None
        assert found_album.id == album.id
        assert found_album.name == "Test Album"

    def test_get_by_id_non_existing(self, repo: AlbumRepository):
        """ID로 존재하지 않는 앨범 조회 테스트"""
        found_album = repo.get_by_id(999)
        assert found_album is None

    def test_get_by_id_inactive_album(self, repo: AlbumRepository, test_user: User):
        """비활성화된 앨범 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 앨범 비활성화
        album.is_active = False
        repo.db.commit()

        # 조회 시 None 반환
        found_album = repo.get_by_id(album.id)
        assert found_album is None

    def test_get_albums_no_filters(self, repo: AlbumRepository, test_user: User):
        """필터 없이 앨범 목록 조회 테스트"""
        # 여러 앨범 생성
        album1 = repo.create({
            "name": "Album 1",
            "album_type": "personal",
            "created_by_id": test_user.id
        })
        album2 = repo.create({
            "name": "Album 2",
            "album_type": "group",
            "created_by_id": test_user.id
        })

        albums = repo.get_albums()

        assert len(albums) == 2
        assert album1 in albums
        assert album2 in albums

    def test_get_albums_by_created_by_id(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """생성자 ID로 앨범 목록 조회 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # 각 사용자가 앨범 생성
        album1 = repo.create({
            "name": "User Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })
        repo.create({
            "name": "Other Album",
            "album_type": "personal",
            "created_by_id": other_user.id
        })

        albums = repo.get_albums(created_by_id=test_user.id)

        assert len(albums) == 1
        assert albums[0] == album1

    def test_get_albums_by_group_id(self, repo: AlbumRepository, test_user: User, test_group: Group):
        """그룹 ID로 앨범 목록 조회 테스트"""
        album1 = repo.create({
            "name": "Group Album",
            "album_type": "group",
            "created_by_id": test_user.id,
            "group_id": test_group.id
        })
        repo.create({
            "name": "Personal Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        albums = repo.get_albums(group_id=test_group.id)

        assert len(albums) == 1
        assert albums[0] == album1

    def test_get_albums_by_album_type(self, repo: AlbumRepository, test_user: User):
        """앨범 타입으로 앨범 목록 조회 테스트"""
        album1 = repo.create({
            "name": "Personal Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })
        repo.create({
            "name": "Group Album",
            "album_type": "group",
            "created_by_id": test_user.id
        })

        albums = repo.get_albums(album_type="personal")

        assert len(albums) == 1
        assert albums[0] == album1

    def test_get_albums_pagination(self, repo: AlbumRepository, test_user: User):
        """앨범 목록 페이지네이션 테스트"""
        # 여러 앨범 생성
        for i in range(5):
            repo.create({
                "name": f"Album {i}",
                "album_type": "personal",
                "created_by_id": test_user.id
            })

        albums_page1 = repo.get_albums(skip=0, limit=2)
        albums_page2 = repo.get_albums(skip=2, limit=2)

        assert len(albums_page1) == 2
        assert len(albums_page2) == 2
        assert albums_page1[0] != albums_page2[0]

    def test_update_existing_album(self, repo: AlbumRepository, test_user: User):
        """기존 앨범 업데이트 테스트"""
        album = repo.create({
            "name": "Original Name",
            "description": "Original Description",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        update_data = {
            "name": "Updated Name",
            "description": "Updated Description",
            "is_public": True
        }

        updated_album = repo.update(album.id, update_data)

        assert updated_album is not None
        assert updated_album.name == "Updated Name"
        assert updated_album.description == "Updated Description"
        assert updated_album.is_public is True

    def test_update_non_existing_album(self, repo: AlbumRepository):
        """존재하지 않는 앨범 업데이트 테스트"""
        update_data = {"name": "Updated Name"}
        updated_album = repo.update(999, update_data)
        assert updated_album is None

    def test_update_invalid_field(self, repo: AlbumRepository, test_user: User):
        """잘못된 필드로 앨범 업데이트 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        update_data = {
            "name": "Updated Name",
            "invalid_field": "Invalid Value"
        }

        updated_album = repo.update(album.id, update_data)

        assert updated_album is not None
        assert updated_album.name == "Updated Name"
        assert not hasattr(updated_album, "invalid_field")

    def test_delete_existing_album(self, repo: AlbumRepository, test_user: User):
        """기존 앨범 삭제 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        result = repo.delete(album.id)

        assert result is True

        # 앨범이 소프트 삭제되었는지 확인
        deleted_album = repo.get_by_id(album.id)
        assert deleted_album is None

    def test_delete_non_existing_album(self, repo: AlbumRepository):
        """존재하지 않는 앨범 삭제 테스트"""
        result = repo.delete(999)
        assert result is False

    def test_add_photo_to_album(self, repo: AlbumRepository, test_user: User, test_photo: Photo):
        """앨범에 사진 추가 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        result = repo.add_photo_to_album(album.id, test_photo.id)

        assert result is True
        assert repo.is_photo_in_album(album.id, test_photo.id) is True

    def test_add_duplicate_photo_to_album(self, repo: AlbumRepository, test_user: User, test_photo: Photo):
        """앨범에 중복 사진 추가 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 첫 번째 추가
        result1 = repo.add_photo_to_album(album.id, test_photo.id)
        # 두 번째 추가 (중복)
        result2 = repo.add_photo_to_album(album.id, test_photo.id)

        assert result1 is True
        assert result2 is False

    def test_remove_photo_from_album(self, repo: AlbumRepository, test_user: User, test_photo: Photo):
        """앨범에서 사진 제거 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 사진 추가 후 제거
        repo.add_photo_to_album(album.id, test_photo.id)
        result = repo.remove_photo_from_album(album.id, test_photo.id)

        assert result is True
        assert repo.is_photo_in_album(album.id, test_photo.id) is False

    def test_remove_non_existing_photo_from_album(self, repo: AlbumRepository, test_user: User):
        """앨범에서 존재하지 않는 사진 제거 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        result = repo.remove_photo_from_album(album.id, 999)
        assert result is False

    def test_is_photo_in_album(self, repo: AlbumRepository, test_user: User, test_photo: Photo):
        """사진이 앨범에 있는지 확인 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 사진이 없을 때
        assert repo.is_photo_in_album(album.id, test_photo.id) is False

        # 사진 추가 후
        repo.add_photo_to_album(album.id, test_photo.id)
        assert repo.is_photo_in_album(album.id, test_photo.id) is True

    def test_get_album_photos(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """앨범의 사진 목록 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 여러 사진 생성 및 추가
        photos = []
        for i in range(3):
            photo = Photo(
                filename=f"test{i}.jpg",
                file_path=f"/test/path{i}",
                file_size=1024,
                width=800,
                height=600,
                uploaded_by_id=test_user.id
            )
            db_session.add(photo)
            db_session.commit()
            db_session.refresh(photo)
            photos.append(photo)
            repo.add_photo_to_album(album.id, photo.id)

        album_photos = repo.get_album_photos(album.id)

        assert len(album_photos) == 3
        for photo in photos:
            assert photo in album_photos

    def test_get_album_photos_with_inactive_photos(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """비활성화된 사진이 포함된 앨범의 사진 목록 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 활성화된 사진
        active_photo = Photo(
            filename="active.jpg",
            file_path="/test/active",
            file_size=1024,
            width=800,
            height=600,
            uploaded_by_id=test_user.id
        )
        db_session.add(active_photo)
        db_session.commit()
        db_session.refresh(active_photo)

        # 비활성화된 사진
        inactive_photo = Photo(
            filename="inactive.jpg",
            file_path="/test/inactive",
            file_size=1024,
            width=800,
            height=600,
            uploaded_by_id=test_user.id,
            is_active=False
        )
        db_session.add(inactive_photo)
        db_session.commit()
        db_session.refresh(inactive_photo)

        # 앨범에 두 사진 모두 추가
        repo.add_photo_to_album(album.id, active_photo.id)
        repo.add_photo_to_album(album.id, inactive_photo.id)

        album_photos = repo.get_album_photos(album.id)

        # 활성화된 사진만 반환되어야 함
        assert len(album_photos) == 1
        assert active_photo in album_photos
        assert inactive_photo not in album_photos

    def test_get_album_photo_count(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """앨범의 사진 개수 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 초기 개수
        count = repo.get_album_photo_count(album.id)
        assert count == 0

        # 사진 추가
        for i in range(3):
            photo = Photo(
                filename=f"test{i}.jpg",
                file_path=f"/test/path{i}",
                file_size=1024,
                width=800,
                height=600,
                uploaded_by_id=test_user.id
            )
            db_session.add(photo)
            db_session.commit()
            db_session.refresh(photo)
            repo.add_photo_to_album(album.id, photo.id)

        count = repo.get_album_photo_count(album.id)
        assert count == 3

    def test_create_album_share(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """앨범 공유 생성 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 공유할 사용자 생성
        shared_user = User(
            email="shared@example.com",
            username="shareduser",
            hashed_password="hashed_password"
        )
        db_session.add(shared_user)
        db_session.commit()
        db_session.refresh(shared_user)

        share_data = {
            "album_id": album.id,
            "shared_with_id": shared_user.id,
            "permission": "view"
        }

        share = repo.create_album_share(share_data)

        assert share.id is not None
        assert share.album_id == album.id
        assert share.shared_with_id == shared_user.id
        assert share.permission == "view"
        assert share.is_active is True

    def test_get_album_share(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """특정 사용자와의 앨범 공유 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        shared_user = User(
            email="shared@example.com",
            username="shareduser",
            hashed_password="hashed_password"
        )
        db_session.add(shared_user)
        db_session.commit()
        db_session.refresh(shared_user)

        # 공유 생성
        share = repo.create_album_share({
            "album_id": album.id,
            "shared_with_id": shared_user.id,
            "permission": "edit"
        })

        # 공유 조회
        found_share = repo.get_album_share(album.id, shared_user.id)

        assert found_share is not None
        assert found_share.id == share.id
        assert found_share.permission == "edit"

    def test_get_album_share_non_existing(self, repo: AlbumRepository, test_user: User):
        """존재하지 않는 앨범 공유 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        found_share = repo.get_album_share(album.id, 999)
        assert found_share is None

    def test_get_album_shares(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """앨범의 모든 공유 목록 조회 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        # 여러 사용자와 공유
        shared_users = []
        for i in range(3):
            user = User(
                email=f"shared{i}@example.com",
                username=f"shareduser{i}",
                hashed_password="hashed_password"
            )
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            shared_users.append(user)

            repo.create_album_share({
                "album_id": album.id,
                "shared_with_id": user.id,
                "permission": "view"
            })

        shares = repo.get_album_shares(album.id)

        assert len(shares) == 3
        shared_user_ids = [share.shared_with_id for share in shares]
        for user in shared_users:
            assert user.id in shared_user_ids

    def test_get_shared_albums(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """사용자가 공유받은 앨범 목록 조회 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # 다른 사용자가 앨범 생성
        albums = []
        for i in range(2):
            album = repo.create({
                "name": f"Shared Album {i}",
                "album_type": "personal",
                "created_by_id": other_user.id
            })
            albums.append(album)

            # test_user와 공유
            repo.create_album_share({
                "album_id": album.id,
                "shared_with_id": test_user.id,
                "permission": "view"
            })

        shared_albums = repo.get_shared_albums(test_user.id)

        assert len(shared_albums) == 2
        album_ids = [share.album_id for share in shared_albums]
        for album in albums:
            assert album.id in album_ids

    def test_update_album_share(self, repo: AlbumRepository, test_user: User, db_session: Session):
        """앨범 공유 정보 수정 테스트"""
        album = repo.create({
            "name": "Test Album",
            "album_type": "personal",
            "created_by_id": test_user.id
        })

        shared_user = User(
            email="shared@example.com",
            username="shareduser",
            hashed_password="hashed_password"
        )
        db_session.add(shared_user)
        db_session.commit()
        db_session.refresh(shared_user)

        share = repo.create_album_share({
            "album_id": album.id,
            "shared_with_id": shared_user.id,
            "permission": "view"
        })

        # 권한 업데이트
        updated_share = repo.update_album_share(share.id, {"permission": "edit"})

        assert updated_share is not None
        assert updated_share.permission == "edit"

    def test_update_album_share_non_existing(self, repo: AlbumRepository):
        """존재하지 않는 앨범 공유 정보 수정 테스트"""
        updated_share = repo.update_album_share(999, {"permission": "edit"})
        assert updated_share is None

    def test_get_public_albums(self, repo: AlbumRepository, test_user: User):
        """공개 앨범 목록 조회 테스트"""
        # 공개 앨범 생성
        public_album = repo.create({
            "name": "Public Album",
            "album_type": "personal",
            "created_by_id": test_user.id,
            "is_public": True
        })

        # 비공개 앨범 생성
        repo.create({
            "name": "Private Album",
            "album_type": "personal",
            "created_by_id": test_user.id,
            "is_public": False
        })

        public_albums = repo.get_public_albums()

        assert len(public_albums) == 1
        assert public_albums[0] == public_album
        assert public_albums[0].is_public is True

    def test_get_public_albums_pagination(self, repo: AlbumRepository, test_user: User):
        """공개 앨범 목록 페이지네이션 테스트"""
        # 여러 공개 앨범 생성
        for i in range(5):
            repo.create({
                "name": f"Public Album {i}",
                "album_type": "personal",
                "created_by_id": test_user.id,
                "is_public": True
            })

        albums_page1 = repo.get_public_albums(skip=0, limit=2)
        albums_page2 = repo.get_public_albums(skip=2, limit=2)

        assert len(albums_page1) == 2
        assert len(albums_page2) == 2
        assert albums_page1[0] != albums_page2[0]