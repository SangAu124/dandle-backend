import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.infra.photo_repository import PhotoRepository
from app.domain.photo import Photo, PhotoTag
from app.domain.user import User
from app.domain.group import Group


class TestPhotoRepository:
    """PhotoRepository 테스트"""

    @pytest.fixture
    def repo(self, db_session: Session):
        """Repository fixture"""
        return PhotoRepository(db_session)

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

    def test_create(self, repo: PhotoRepository, test_user: User):
        """사진 생성 테스트"""
        photo_data = {
            "filename": "test.jpg",
            "original_filename": "original_test.jpg",
            "file_path": "/test/path/test.jpg",
            "file_size": 1024000,
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "s3_bucket": "test-bucket",
            "s3_key": "photos/test.jpg",
            "s3_url": "https://test-bucket.s3.amazonaws.com/photos/test.jpg",
            "uploaded_by_id": test_user.id,
            "file_hash": "abc123def456"
        }

        photo = repo.create(photo_data)

        assert photo.id is not None
        assert photo.filename == "test.jpg"
        assert photo.original_filename == "original_test.jpg"
        assert photo.file_path == "/test/path/test.jpg"
        assert photo.file_size == 1024000
        assert photo.width == 1920
        assert photo.height == 1080
        assert photo.format == "JPEG"
        assert photo.uploaded_by_id == test_user.id
        assert photo.is_active is True
        assert photo.is_processed is False

    def test_get_by_id_existing(self, repo: PhotoRepository, test_user: User):
        """ID로 기존 사진 조회 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id
        })

        found_photo = repo.get_by_id(photo.id)

        assert found_photo is not None
        assert found_photo.id == photo.id
        assert found_photo.filename == "test.jpg"

    def test_get_by_id_non_existing(self, repo: PhotoRepository):
        """존재하지 않는 사진 조회 테스트"""
        found_photo = repo.get_by_id(999)
        assert found_photo is None

    def test_get_by_id_inactive(self, repo: PhotoRepository, test_user: User):
        """비활성화된 사진 조회 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id
        })

        # 사진 비활성화
        photo.is_active = False
        repo.db.commit()

        found_photo = repo.get_by_id(photo.id)
        assert found_photo is None

    def test_get_by_hash(self, repo: PhotoRepository, test_user: User):
        """파일 해시로 사진 조회 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id,
            "file_hash": "unique_hash_123"
        })

        found_photo = repo.get_by_hash("unique_hash_123")

        assert found_photo is not None
        assert found_photo.id == photo.id
        assert found_photo.file_hash == "unique_hash_123"

    def test_get_by_hash_non_existing(self, repo: PhotoRepository):
        """존재하지 않는 해시로 사진 조회 테스트"""
        found_photo = repo.get_by_hash("non_existing_hash")
        assert found_photo is None

    def test_get_photos_no_filters(self, repo: PhotoRepository, test_user: User):
        """필터 없이 사진 목록 조회 테스트"""
        # 여러 사진 생성
        photo1 = repo.create({
            "filename": "photo1.jpg",
            "original_filename": "photo1.jpg",
            "file_path": "/test/path1",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "photo1.jpg",
            "s3_url": "https://test.com/photo1.jpg",
            "uploaded_by_id": test_user.id
        })
        photo2 = repo.create({
            "filename": "photo2.jpg",
            "original_filename": "photo2.jpg",
            "file_path": "/test/path2",
            "file_size": 2048,
            "s3_bucket": "test-bucket",
            "s3_key": "photo2.jpg",
            "s3_url": "https://test.com/photo2.jpg",
            "uploaded_by_id": test_user.id
        })

        photos = repo.get_photos()

        assert len(photos) == 2
        assert photo1 in photos
        assert photo2 in photos

    def test_get_photos_by_group_id(self, repo: PhotoRepository, test_user: User, test_group: Group):
        """그룹 ID로 사진 목록 조회 테스트"""
        # 그룹 사진
        group_photo = repo.create({
            "filename": "group_photo.jpg",
            "original_filename": "group_photo.jpg",
            "file_path": "/test/group_path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "group_photo.jpg",
            "s3_url": "https://test.com/group_photo.jpg",
            "uploaded_by_id": test_user.id,
            "group_id": test_group.id
        })

        # 개인 사진
        repo.create({
            "filename": "personal_photo.jpg",
            "original_filename": "personal_photo.jpg",
            "file_path": "/test/personal_path",
            "file_size": 2048,
            "s3_bucket": "test-bucket",
            "s3_key": "personal_photo.jpg",
            "s3_url": "https://test.com/personal_photo.jpg",
            "uploaded_by_id": test_user.id
        })

        photos = repo.get_photos(group_id=test_group.id)

        assert len(photos) == 1
        assert photos[0] == group_photo

    def test_get_photos_by_uploaded_by_id(self, repo: PhotoRepository, test_user: User, db_session: Session):
        """업로더 ID로 사진 목록 조회 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # 각 사용자가 사진 업로드
        user_photo = repo.create({
            "filename": "user_photo.jpg",
            "original_filename": "user_photo.jpg",
            "file_path": "/test/user_path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "user_photo.jpg",
            "s3_url": "https://test.com/user_photo.jpg",
            "uploaded_by_id": test_user.id
        })

        repo.create({
            "filename": "other_photo.jpg",
            "original_filename": "other_photo.jpg",
            "file_path": "/test/other_path",
            "file_size": 2048,
            "s3_bucket": "test-bucket",
            "s3_key": "other_photo.jpg",
            "s3_url": "https://test.com/other_photo.jpg",
            "uploaded_by_id": other_user.id
        })

        photos = repo.get_photos(uploaded_by_id=test_user.id)

        assert len(photos) == 1
        assert photos[0] == user_photo

    def test_get_photos_pagination(self, repo: PhotoRepository, test_user: User):
        """사진 목록 페이지네이션 테스트"""
        # 여러 사진 생성
        for i in range(5):
            repo.create({
                "filename": f"photo{i}.jpg",
                "original_filename": f"photo{i}.jpg",
                "file_path": f"/test/path{i}",
                "file_size": 1024,
                "s3_bucket": "test-bucket",
                "s3_key": f"photo{i}.jpg",
                "s3_url": f"https://test.com/photo{i}.jpg",
                "uploaded_by_id": test_user.id
            })

        photos_page1 = repo.get_photos(skip=0, limit=2)
        photos_page2 = repo.get_photos(skip=2, limit=2)

        assert len(photos_page1) == 2
        assert len(photos_page2) == 2
        assert photos_page1[0] != photos_page2[0]

    def test_get_unprocessed_photos(self, repo: PhotoRepository, test_user: User):
        """처리되지 않은 사진 목록 조회 테스트"""
        # 처리된 사진
        repo.create({
            "filename": "processed.jpg",
            "original_filename": "processed.jpg",
            "file_path": "/test/processed",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "processed.jpg",
            "s3_url": "https://test.com/processed.jpg",
            "uploaded_by_id": test_user.id,
            "is_processed": True
        })

        # 미처리 사진들
        unprocessed1 = repo.create({
            "filename": "unprocessed1.jpg",
            "original_filename": "unprocessed1.jpg",
            "file_path": "/test/unprocessed1",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "unprocessed1.jpg",
            "s3_url": "https://test.com/unprocessed1.jpg",
            "uploaded_by_id": test_user.id,
            "is_processed": False
        })

        unprocessed2 = repo.create({
            "filename": "unprocessed2.jpg",
            "original_filename": "unprocessed2.jpg",
            "file_path": "/test/unprocessed2",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "unprocessed2.jpg",
            "s3_url": "https://test.com/unprocessed2.jpg",
            "uploaded_by_id": test_user.id,
            "is_processed": False
        })

        photos = repo.get_unprocessed_photos()

        assert len(photos) == 2
        assert unprocessed1 in photos
        assert unprocessed2 in photos

    def test_get_unprocessed_photos_limit(self, repo: PhotoRepository, test_user: User):
        """처리되지 않은 사진 목록 제한 테스트"""
        # 여러 미처리 사진 생성
        for i in range(5):
            repo.create({
                "filename": f"unprocessed{i}.jpg",
                "original_filename": f"unprocessed{i}.jpg",
                "file_path": f"/test/unprocessed{i}",
                "file_size": 1024,
                "s3_bucket": "test-bucket",
                "s3_key": f"unprocessed{i}.jpg",
                "s3_url": f"https://test.com/unprocessed{i}.jpg",
                "uploaded_by_id": test_user.id,
                "is_processed": False
            })

        photos = repo.get_unprocessed_photos(limit=3)
        assert len(photos) == 3

    def test_update_existing_photo(self, repo: PhotoRepository, test_user: User):
        """기존 사진 업데이트 테스트"""
        photo = repo.create({
            "filename": "original.jpg",
            "original_filename": "original.jpg",
            "file_path": "/test/original",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "original.jpg",
            "s3_url": "https://test.com/original.jpg",
            "uploaded_by_id": test_user.id,
            "is_processed": False
        })

        update_data = {
            "is_processed": True,
            "width": 1920,
            "height": 1080,
            "format": "JPEG"
        }

        updated_photo = repo.update(photo.id, update_data)

        assert updated_photo is not None
        assert updated_photo.is_processed is True
        assert updated_photo.width == 1920
        assert updated_photo.height == 1080
        assert updated_photo.format == "JPEG"

    def test_update_non_existing_photo(self, repo: PhotoRepository):
        """존재하지 않는 사진 업데이트 테스트"""
        update_data = {"is_processed": True}
        updated_photo = repo.update(999, update_data)
        assert updated_photo is None

    def test_delete_existing_photo(self, repo: PhotoRepository, test_user: User):
        """기존 사진 삭제 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id
        })

        result = repo.delete(photo.id)

        assert result is True
        # 소프트 삭제 확인
        deleted_photo = repo.get_by_id(photo.id)
        assert deleted_photo is None

    def test_delete_non_existing_photo(self, repo: PhotoRepository):
        """존재하지 않는 사진 삭제 테스트"""
        result = repo.delete(999)
        assert result is False

    def test_create_tag(self, repo: PhotoRepository, test_user: User):
        """사진 태그 생성 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id
        })

        tag_data = {
            "photo_id": photo.id,
            "tag_name": "landscape",
            "confidence": 0.95
        }

        tag = repo.create_tag(tag_data)

        assert tag.id is not None
        assert tag.photo_id == photo.id
        assert tag.tag_name == "landscape"
        assert tag.confidence == 0.95

    def test_get_photo_tags(self, repo: PhotoRepository, test_user: User):
        """사진의 태그 목록 조회 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id
        })

        # 여러 태그 생성
        tag1 = repo.create_tag({
            "photo_id": photo.id,
            "tag_name": "landscape",
            "confidence": 0.95
        })

        tag2 = repo.create_tag({
            "photo_id": photo.id,
            "tag_name": "nature",
            "confidence": 0.87
        })

        tag3 = repo.create_tag({
            "photo_id": photo.id,
            "tag_name": "mountain",
            "confidence": 0.92
        })

        tags = repo.get_photo_tags(photo.id)

        assert len(tags) == 3
        assert tag1 in tags
        assert tag2 in tags
        assert tag3 in tags
        # 신뢰도 순으로 정렬되어야 함
        assert tags[0].confidence >= tags[1].confidence >= tags[2].confidence

    def test_delete_photo_tag(self, repo: PhotoRepository, test_user: User):
        """사진 태그 삭제 테스트"""
        photo = repo.create({
            "filename": "test.jpg",
            "original_filename": "test.jpg",
            "file_path": "/test/path",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "test.jpg",
            "s3_url": "https://test.com/test.jpg",
            "uploaded_by_id": test_user.id
        })

        tag = repo.create_tag({
            "photo_id": photo.id,
            "tag_name": "landscape",
            "confidence": 0.95
        })

        result = repo.delete_photo_tag(tag.id)

        assert result is True
        # 태그가 삭제되었는지 확인
        remaining_tags = repo.get_photo_tags(photo.id)
        assert len(remaining_tags) == 0

    def test_delete_photo_tag_non_existing(self, repo: PhotoRepository):
        """존재하지 않는 사진 태그 삭제 테스트"""
        result = repo.delete_photo_tag(999)
        assert result is False

    def test_search_photos_by_tag(self, repo: PhotoRepository, test_user: User):
        """태그로 사진 검색 테스트"""
        # 사진들 생성
        photo1 = repo.create({
            "filename": "landscape1.jpg",
            "original_filename": "landscape1.jpg",
            "file_path": "/test/landscape1",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "landscape1.jpg",
            "s3_url": "https://test.com/landscape1.jpg",
            "uploaded_by_id": test_user.id
        })

        photo2 = repo.create({
            "filename": "landscape2.jpg",
            "original_filename": "landscape2.jpg",
            "file_path": "/test/landscape2",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "landscape2.jpg",
            "s3_url": "https://test.com/landscape2.jpg",
            "uploaded_by_id": test_user.id
        })

        photo3 = repo.create({
            "filename": "portrait.jpg",
            "original_filename": "portrait.jpg",
            "file_path": "/test/portrait",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "portrait.jpg",
            "s3_url": "https://test.com/portrait.jpg",
            "uploaded_by_id": test_user.id
        })

        # 태그들 생성
        repo.create_tag({
            "photo_id": photo1.id,
            "tag_name": "landscape",
            "confidence": 0.95
        })

        repo.create_tag({
            "photo_id": photo2.id,
            "tag_name": "mountain_landscape",
            "confidence": 0.87
        })

        repo.create_tag({
            "photo_id": photo3.id,
            "tag_name": "portrait",
            "confidence": 0.92
        })

        # "landscape"를 포함하는 태그로 검색
        photos = repo.search_photos_by_tag("landscape")

        assert len(photos) == 2
        assert photo1 in photos
        assert photo2 in photos
        assert photo3 not in photos

    def test_get_photos_by_date_range(self, repo: PhotoRepository, test_user: User):
        """날짜 범위로 사진 조회 테스트"""
        # 날짜가 다른 사진들 생성
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mid_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
        end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
        outside_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        photo1 = repo.create({
            "filename": "photo1.jpg",
            "original_filename": "photo1.jpg",
            "file_path": "/test/photo1",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "photo1.jpg",
            "s3_url": "https://test.com/photo1.jpg",
            "uploaded_by_id": test_user.id,
            "taken_at": start_date
        })

        photo2 = repo.create({
            "filename": "photo2.jpg",
            "original_filename": "photo2.jpg",
            "file_path": "/test/photo2",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "photo2.jpg",
            "s3_url": "https://test.com/photo2.jpg",
            "uploaded_by_id": test_user.id,
            "taken_at": mid_date
        })

        photo3 = repo.create({
            "filename": "photo3.jpg",
            "original_filename": "photo3.jpg",
            "file_path": "/test/photo3",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "photo3.jpg",
            "s3_url": "https://test.com/photo3.jpg",
            "uploaded_by_id": test_user.id,
            "taken_at": outside_date
        })

        # 2023년 사진들 조회
        photos = repo.get_photos_by_date_range(start_date, end_date)

        assert len(photos) == 2
        assert photo1 in photos
        assert photo2 in photos
        assert photo3 not in photos

    def test_get_photos_by_date_range_with_group(self, repo: PhotoRepository, test_user: User, test_group: Group):
        """그룹 필터와 함께 날짜 범위로 사진 조회 테스트"""
        date = datetime(2023, 6, 15, tzinfo=timezone.utc)

        # 그룹 사진
        group_photo = repo.create({
            "filename": "group_photo.jpg",
            "original_filename": "group_photo.jpg",
            "file_path": "/test/group_photo",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "group_photo.jpg",
            "s3_url": "https://test.com/group_photo.jpg",
            "uploaded_by_id": test_user.id,
            "group_id": test_group.id,
            "taken_at": date
        })

        # 개인 사진
        repo.create({
            "filename": "personal_photo.jpg",
            "original_filename": "personal_photo.jpg",
            "file_path": "/test/personal_photo",
            "file_size": 1024,
            "s3_bucket": "test-bucket",
            "s3_key": "personal_photo.jpg",
            "s3_url": "https://test.com/personal_photo.jpg",
            "uploaded_by_id": test_user.id,
            "taken_at": date
        })

        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

        photos = repo.get_photos_by_date_range(start_date, end_date, group_id=test_group.id)

        assert len(photos) == 1
        assert photos[0] == group_photo