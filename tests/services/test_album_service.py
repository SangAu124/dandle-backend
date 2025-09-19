import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.album_service import AlbumService
from app.domain.album import Album, AlbumShare
from app.domain.user import User


class TestAlbumService:
    """AlbumService 테스트"""

    @pytest.fixture
    def mock_repo(self):
        """Mock repository fixture"""
        return Mock()

    @pytest.fixture
    def service(self, db_session: Session):
        """Service fixture"""
        return AlbumService(db_session)

    @pytest.fixture
    def mock_service(self, mock_repo):
        """Service with mock repository"""
        service = AlbumService(Mock())
        service.repository = mock_repo
        return service

    @pytest.fixture
    def sample_album(self):
        """Sample album fixture"""
        return Album(
            id=1,
            name="Test Album",
            description="Test Description",
            album_type="personal",
            created_by_id=1,
            is_active=True,
            is_public=False
        )

    @pytest.fixture
    def sample_album_share(self):
        """Sample album share fixture"""
        return AlbumShare(
            id=1,
            album_id=1,
            shared_with_id=2,
            permission="view",
            is_active=True
        )

    def test_create_album(self, mock_service, mock_repo, sample_album):
        """앨범 생성 테스트"""
        mock_repo.create.return_value = sample_album

        result = mock_service.create_album(
            name="Test Album",
            created_by_id=1,
            album_type="personal",
            description="Test Description"
        )

        assert result == sample_album
        mock_repo.create.assert_called_once_with({
            "name": "Test Album",
            "description": "Test Description",
            "album_type": "personal",
            "auto_criteria": None,
            "is_public": False,
            "created_by_id": 1,
            "group_id": None,
            "is_active": True
        })

    def test_create_album_with_group(self, mock_service, mock_repo, sample_album):
        """그룹 앨범 생성 테스트"""
        mock_repo.create.return_value = sample_album

        result = mock_service.create_album(
            name="Group Album",
            created_by_id=1,
            album_type="group",
            group_id=5,
            is_public=True
        )

        assert result == sample_album
        mock_repo.create.assert_called_once_with({
            "name": "Group Album",
            "description": None,
            "album_type": "group",
            "auto_criteria": None,
            "is_public": True,
            "created_by_id": 1,
            "group_id": 5,
            "is_active": True
        })

    def test_create_auto_album(self, mock_service, mock_repo, sample_album):
        """자동 앨범 생성 테스트"""
        sample_album.album_type = "auto"
        sample_album.auto_criteria = "face:123"
        mock_repo.create.return_value = sample_album

        result = mock_service.create_auto_album(
            name="Face Album",
            created_by_id=1,
            criteria="face:123",
            group_id=5
        )

        assert result == sample_album
        mock_repo.create.assert_called_once_with({
            "name": "Face Album",
            "description": None,
            "album_type": "auto",
            "auto_criteria": "face:123",
            "is_public": False,
            "created_by_id": 1,
            "group_id": 5,
            "is_active": True
        })

    def test_get_album_by_id_existing(self, mock_service, mock_repo, sample_album):
        """기존 앨범 조회 테스트"""
        mock_repo.get_by_id.return_value = sample_album

        result = mock_service.get_album_by_id(1)

        assert result == sample_album
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_album_by_id_non_existing(self, mock_service, mock_repo):
        """존재하지 않는 앨범 조회 테스트"""
        mock_repo.get_by_id.return_value = None

        result = mock_service.get_album_by_id(999)

        assert result is None
        mock_repo.get_by_id.assert_called_once_with(999)

    def test_get_albums(self, mock_service, mock_repo, sample_album):
        """앨범 목록 조회 테스트"""
        mock_repo.get_albums.return_value = [sample_album]

        result = mock_service.get_albums(
            created_by_id=1,
            group_id=5,
            album_type="personal",
            skip=10,
            limit=20
        )

        assert result == [sample_album]
        mock_repo.get_albums.assert_called_once_with(
            created_by_id=1,
            group_id=5,
            album_type="personal",
            skip=10,
            limit=20
        )

    def test_get_albums_default_params(self, mock_service, mock_repo, sample_album):
        """기본 매개변수로 앨범 목록 조회 테스트"""
        mock_repo.get_albums.return_value = [sample_album]

        result = mock_service.get_albums()

        assert result == [sample_album]
        mock_repo.get_albums.assert_called_once_with(
            created_by_id=None,
            group_id=None,
            album_type=None,
            skip=0,
            limit=50
        )

    def test_get_user_albums(self, mock_service, mock_repo, sample_album, sample_album_share):
        """사용자의 모든 앨범 조회 테스트"""
        # 생성한 앨범
        created_album = Album(id=1, name="Created Album", album_type="personal", created_by_id=1)
        # 공유받은 앨범
        shared_album = Album(id=2, name="Shared Album", album_type="personal", created_by_id=2)

        sample_album_share.album = shared_album

        mock_repo.get_albums.return_value = [created_album]
        mock_repo.get_shared_albums.return_value = [sample_album_share]

        result = mock_service.get_user_albums(1)

        assert len(result) == 2
        assert created_album in result
        assert shared_album in result
        mock_repo.get_albums.assert_called_once_with(created_by_id=1)
        mock_repo.get_shared_albums.assert_called_once_with(1)

    def test_get_user_albums_no_duplicates(self, mock_service, mock_repo, sample_album, sample_album_share):
        """사용자 앨범 조회 시 중복 제거 테스트"""
        # 같은 앨범이 생성 목록과 공유 목록에 모두 있는 경우
        album = Album(id=1, name="Album", album_type="personal", created_by_id=1)
        sample_album_share.album = album

        mock_repo.get_albums.return_value = [album]
        mock_repo.get_shared_albums.return_value = [sample_album_share]

        result = mock_service.get_user_albums(1)

        assert len(result) == 1
        assert album in result

    def test_update_album(self, mock_service, mock_repo, sample_album):
        """앨범 정보 수정 테스트"""
        update_data = {"name": "Updated Name", "description": "Updated Description"}
        updated_album = Album(id=1, name="Updated Name", description="Updated Description")
        mock_repo.update.return_value = updated_album

        result = mock_service.update_album(1, update_data)

        assert result == updated_album
        mock_repo.update.assert_called_once_with(1, update_data)

    def test_update_album_non_existing(self, mock_service, mock_repo):
        """존재하지 않는 앨범 수정 테스트"""
        mock_repo.update.return_value = None

        result = mock_service.update_album(999, {"name": "New Name"})

        assert result is None
        mock_repo.update.assert_called_once_with(999, {"name": "New Name"})

    def test_delete_album(self, mock_service, mock_repo):
        """앨범 삭제 테스트"""
        mock_repo.delete.return_value = True

        result = mock_service.delete_album(1)

        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_album_non_existing(self, mock_service, mock_repo):
        """존재하지 않는 앨범 삭제 테스트"""
        mock_repo.delete.return_value = False

        result = mock_service.delete_album(999)

        assert result is False
        mock_repo.delete.assert_called_once_with(999)

    def test_add_photos_to_album_success(self, mock_service, mock_repo, sample_album):
        """앨범에 사진들 추가 성공 테스트"""
        mock_repo.get_by_id.return_value = sample_album
        mock_repo.is_photo_in_album.side_effect = [False, False, True]  # 첫 두 개는 없고, 세 번째는 이미 있음
        mock_repo.add_photo_to_album.return_value = True

        result = mock_service.add_photos_to_album(1, [101, 102, 103])

        assert result is True
        mock_repo.get_by_id.assert_called_once_with(1)
        assert mock_repo.is_photo_in_album.call_count == 3
        assert mock_repo.add_photo_to_album.call_count == 2  # 첫 두 개만 추가

    def test_add_photos_to_album_album_not_found(self, mock_service, mock_repo):
        """존재하지 않는 앨범에 사진 추가 테스트"""
        mock_repo.get_by_id.return_value = None

        result = mock_service.add_photos_to_album(999, [101, 102])

        assert result is False
        mock_repo.get_by_id.assert_called_once_with(999)
        mock_repo.add_photo_to_album.assert_not_called()

    def test_remove_photo_from_album(self, mock_service, mock_repo):
        """앨범에서 사진 제거 테스트"""
        mock_repo.remove_photo_from_album.return_value = True

        result = mock_service.remove_photo_from_album(1, 101)

        assert result is True
        mock_repo.remove_photo_from_album.assert_called_once_with(1, 101)

    def test_get_album_photos(self, mock_service, mock_repo):
        """앨범의 사진 목록 조회 테스트"""
        photos = [Mock(id=101), Mock(id=102)]
        mock_repo.get_album_photos.return_value = photos

        result = mock_service.get_album_photos(1, skip=10, limit=20)

        assert result == photos
        mock_repo.get_album_photos.assert_called_once_with(1, 10, 20)

    def test_get_album_photos_default_params(self, mock_service, mock_repo):
        """기본 매개변수로 앨범 사진 조회 테스트"""
        photos = [Mock(id=101)]
        mock_repo.get_album_photos.return_value = photos

        result = mock_service.get_album_photos(1)

        assert result == photos
        mock_repo.get_album_photos.assert_called_once_with(1, 0, 50)

    def test_set_cover_photo_success(self, mock_service, mock_repo, sample_album):
        """커버 사진 설정 성공 테스트"""
        mock_repo.is_photo_in_album.return_value = True
        mock_repo.update.return_value = sample_album

        result = mock_service.set_cover_photo(1, 101)

        assert result is True
        mock_repo.is_photo_in_album.assert_called_once_with(1, 101)
        mock_repo.update.assert_called_once_with(1, {"cover_photo_id": 101})

    def test_set_cover_photo_photo_not_in_album(self, mock_service, mock_repo):
        """앨범에 없는 사진을 커버로 설정 시도 테스트"""
        mock_repo.is_photo_in_album.return_value = False

        result = mock_service.set_cover_photo(1, 101)

        assert result is False
        mock_repo.is_photo_in_album.assert_called_once_with(1, 101)
        mock_repo.update.assert_not_called()

    def test_set_cover_photo_update_failed(self, mock_service, mock_repo):
        """커버 사진 설정 업데이트 실패 테스트"""
        mock_repo.is_photo_in_album.return_value = True
        mock_repo.update.return_value = None

        result = mock_service.set_cover_photo(1, 101)

        assert result is False
        mock_repo.update.assert_called_once_with(1, {"cover_photo_id": 101})

    def test_share_album_new_share(self, mock_service, mock_repo, sample_album_share):
        """새로운 앨범 공유 테스트"""
        mock_repo.get_album_share.return_value = None
        mock_repo.create_album_share.return_value = sample_album_share

        result = mock_service.share_album(1, 2, "edit")

        assert result == sample_album_share
        mock_repo.get_album_share.assert_called_once_with(1, 2)
        mock_repo.create_album_share.assert_called_once_with({
            "album_id": 1,
            "shared_with_id": 2,
            "permission": "edit",
            "is_active": True
        })

    def test_share_album_update_existing(self, mock_service, mock_repo, sample_album_share):
        """기존 앨범 공유 업데이트 테스트"""
        existing_share = AlbumShare(id=1, album_id=1, shared_with_id=2, permission="view")
        updated_share = AlbumShare(id=1, album_id=1, shared_with_id=2, permission="edit")

        mock_repo.get_album_share.return_value = existing_share
        mock_repo.update_album_share.return_value = updated_share

        result = mock_service.share_album(1, 2, "edit")

        assert result == updated_share
        mock_repo.get_album_share.assert_called_once_with(1, 2)
        mock_repo.update_album_share.assert_called_once_with(1, {"permission": "edit"})
        mock_repo.create_album_share.assert_not_called()

    def test_share_album_default_permission(self, mock_service, mock_repo, sample_album_share):
        """기본 권한으로 앨범 공유 테스트"""
        mock_repo.get_album_share.return_value = None
        mock_repo.create_album_share.return_value = sample_album_share

        result = mock_service.share_album(1, 2)

        assert result == sample_album_share
        mock_repo.create_album_share.assert_called_once_with({
            "album_id": 1,
            "shared_with_id": 2,
            "permission": "view",
            "is_active": True
        })

    def test_revoke_album_share_success(self, mock_service, mock_repo, sample_album_share):
        """앨범 공유 취소 성공 테스트"""
        mock_repo.get_album_share.return_value = sample_album_share
        mock_repo.update_album_share.return_value = sample_album_share

        result = mock_service.revoke_album_share(1, 2)

        assert result is True
        mock_repo.get_album_share.assert_called_once_with(1, 2)
        mock_repo.update_album_share.assert_called_once_with(1, {"is_active": False})

    def test_revoke_album_share_not_found(self, mock_service, mock_repo):
        """존재하지 않는 앨범 공유 취소 테스트"""
        mock_repo.get_album_share.return_value = None

        result = mock_service.revoke_album_share(1, 2)

        assert result is False
        mock_repo.get_album_share.assert_called_once_with(1, 2)
        mock_repo.update_album_share.assert_not_called()

    def test_revoke_album_share_update_failed(self, mock_service, mock_repo, sample_album_share):
        """앨범 공유 취소 업데이트 실패 테스트"""
        mock_repo.get_album_share.return_value = sample_album_share
        mock_repo.update_album_share.return_value = None

        result = mock_service.revoke_album_share(1, 2)

        assert result is False
        mock_repo.update_album_share.assert_called_once_with(1, {"is_active": False})

    def test_get_album_shares(self, mock_service, mock_repo, sample_album_share):
        """앨범 공유 목록 조회 테스트"""
        shares = [sample_album_share]
        mock_repo.get_album_shares.return_value = shares

        result = mock_service.get_album_shares(1)

        assert result == shares
        mock_repo.get_album_shares.assert_called_once_with(1)

    def test_auto_organize_photos_by_face(self, mock_service, mock_repo, sample_album):
        """얼굴 인식 기반 자동 앨범 생성 테스트"""
        auto_album = Album(
            id=2,
            name="Person 123",
            album_type="auto",
            auto_criteria="face:123",
            created_by_id=1
        )
        mock_repo.create.return_value = auto_album

        result = mock_service.auto_organize_photos_by_face(1, 123)

        assert result == auto_album
        mock_repo.create.assert_called_once_with({
            "name": "Person 123",
            "description": None,
            "album_type": "auto",
            "auto_criteria": "face:123",
            "is_public": False,
            "created_by_id": 1,
            "group_id": None,
            "is_active": True
        })


# Integration tests with real database
def test_album_service_integration(db_session: Session):
    """앨범 서비스 통합 테스트"""
    service = AlbumService(db_session)

    # 테스트 사용자 생성
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 앨범 생성
    album = service.create_album(
        name="Integration Test Album",
        created_by_id=user.id,
        album_type="personal",
        description="Test album for integration"
    )

    assert album.id is not None
    assert album.name == "Integration Test Album"
    assert album.created_by_id == user.id

    # 앨범 조회
    found_album = service.get_album_by_id(album.id)
    assert found_album is not None
    assert found_album.id == album.id

    # 앨범 목록 조회
    albums = service.get_albums(created_by_id=user.id)
    assert len(albums) == 1
    assert albums[0].id == album.id

    # 앨범 업데이트
    updated_album = service.update_album(album.id, {"name": "Updated Album Name"})
    assert updated_album.name == "Updated Album Name"

    # 앨범 삭제
    result = service.delete_album(album.id)
    assert result is True

    # 삭제된 앨범 조회 확인
    deleted_album = service.get_album_by_id(album.id)
    assert deleted_album is None