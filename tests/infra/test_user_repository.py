import pytest
from sqlalchemy.orm import Session
from app.infra.user_repository import UserRepository
from app.domain.user import User


class TestUserRepository:
    """UserRepository 테스트"""

    def test_create(self, db_session: Session):
        """사용자 생성 테스트"""
        repo = UserRepository(db_session)
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password",
            "full_name": "Test User"
        }

        user = repo.create(user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False

    def test_get_by_id_existing(self, db_session: Session):
        """ID로 기존 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # 먼저 사용자 생성
        user = repo.create({
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password"
        })
        db_session.commit()

        # ID로 조회
        found_user = repo.get_by_id(user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "test@example.com"

    def test_get_by_id_non_existing(self, db_session: Session):
        """ID로 존재하지 않는 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        user = repo.get_by_id(999)

        assert user is None

    def test_get_by_email_existing(self, db_session: Session):
        """이메일로 기존 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # 먼저 사용자 생성
        user = repo.create({
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password"
        })
        db_session.commit()

        # 이메일로 조회
        found_user = repo.get_by_email("test@example.com")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "test@example.com"

    def test_get_by_email_non_existing(self, db_session: Session):
        """이메일로 존재하지 않는 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        user = repo.get_by_email("nonexistent@example.com")

        assert user is None

    def test_get_by_username_existing(self, db_session: Session):
        """사용자명으로 기존 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # 먼저 사용자 생성
        user = repo.create({
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password"
        })
        db_session.commit()

        # 사용자명으로 조회
        found_user = repo.get_by_username("testuser")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == "testuser"

    def test_get_by_username_non_existing(self, db_session: Session):
        """사용자명으로 존재하지 않는 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        user = repo.get_by_username("nonexistent_user")

        assert user is None

    def test_get_by_apple_id_existing(self, db_session: Session):
        """Apple ID로 기존 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # Apple ID가 있는 사용자 생성
        user = repo.create({
            "email": "apple@example.com",
            "username": "appleuser",
            "hashed_password": "hashed_password",
            "apple_id": "apple_123"
        })
        db_session.commit()

        # Apple ID로 조회
        found_user = repo.get_by_apple_id("apple_123")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.apple_id == "apple_123"

    def test_get_by_apple_id_non_existing(self, db_session: Session):
        """Apple ID로 존재하지 않는 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        user = repo.get_by_apple_id("nonexistent_apple_id")

        assert user is None

    def test_get_by_google_id_existing(self, db_session: Session):
        """Google ID로 기존 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # Google ID가 있는 사용자 생성
        user = repo.create({
            "email": "google@example.com",
            "username": "googleuser",
            "hashed_password": "hashed_password",
            "google_id": "google_123"
        })
        db_session.commit()

        # Google ID로 조회
        found_user = repo.get_by_google_id("google_123")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.google_id == "google_123"

    def test_get_by_google_id_non_existing(self, db_session: Session):
        """Google ID로 존재하지 않는 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        user = repo.get_by_google_id("nonexistent_google_id")

        assert user is None

    def test_update(self, db_session: Session):
        """사용자 정보 수정 테스트"""
        repo = UserRepository(db_session)

        # 먼저 사용자 생성
        user = repo.create({
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password"
        })
        db_session.commit()

        # 사용자 정보 수정
        updated_user = repo.update(user.id, {
            "full_name": "Updated User",
            "is_verified": True
        })

        assert updated_user is not None
        assert updated_user.full_name == "Updated User"
        assert updated_user.is_verified is True
        assert updated_user.email == "test@example.com"  # 다른 필드는 그대로

    def test_update_non_existing(self, db_session: Session):
        """존재하지 않는 사용자 수정 테스트"""
        repo = UserRepository(db_session)

        updated_user = repo.update(999, {"full_name": "Updated User"})

        assert updated_user is None

    def test_delete(self, db_session: Session):
        """사용자 삭제 테스트"""
        repo = UserRepository(db_session)

        # 먼저 사용자 생성
        user = repo.create({
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password"
        })
        db_session.commit()

        # 사용자 삭제 (소프트 삭제)
        result = repo.delete(user.id)

        assert result is True

        # 소프트 삭제된 사용자는 여전히 존재하지만 is_active가 False
        deleted_user = repo.get_by_id(user.id)
        assert deleted_user is not None
        assert deleted_user.is_active is False

    def test_delete_non_existing(self, db_session: Session):
        """존재하지 않는 사용자 삭제 테스트"""
        repo = UserRepository(db_session)

        result = repo.delete(999)

        assert result is False

    def test_get_all(self, db_session: Session):
        """모든 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # 여러 사용자 생성
        user1 = repo.create({
            "email": "user1@example.com",
            "username": "user1",
            "hashed_password": "password1"
        })
        user2 = repo.create({
            "email": "user2@example.com",
            "username": "user2",
            "hashed_password": "password2"
        })
        db_session.commit()

        # 모든 사용자 조회
        all_users = repo.get_all_active()

        assert len(all_users) >= 2
        user_emails = [user.email for user in all_users]
        assert "user1@example.com" in user_emails
        assert "user2@example.com" in user_emails

    def test_get_all_with_pagination(self, db_session: Session):
        """페이지네이션으로 사용자 조회 테스트"""
        repo = UserRepository(db_session)

        # 여러 사용자 생성
        for i in range(5):
            repo.create({
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "hashed_password": f"password{i}"
            })
        db_session.commit()

        # 페이지네이션으로 조회
        page1_users = repo.get_all_active(skip=0, limit=2)
        page2_users = repo.get_all_active(skip=2, limit=2)

        assert len(page1_users) == 2
        assert len(page2_users) == 2

        # 페이지가 겹치지 않는지 확인
        page1_ids = {user.id for user in page1_users}
        page2_ids = {user.id for user in page2_users}
        assert len(page1_ids.intersection(page2_ids)) == 0