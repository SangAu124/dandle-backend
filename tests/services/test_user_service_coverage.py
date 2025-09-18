import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.domain.user import User


class TestUserServiceCoverage:
    """UserService 커버리지 향상을 위한 테스트"""

    @patch('app.services.user_service.UserRepository')
    def test_get_user_by_email_not_found(self, mock_repo_class, db_session: Session):
        """존재하지 않는 이메일로 사용자 조회 테스트"""
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = None
        mock_repo_class.return_value = mock_repo

        service = UserService(db_session)
        result = service.get_user_by_email("nonexistent@example.com")

        assert result is None
        mock_repo.get_by_email.assert_called_once_with("nonexistent@example.com")

    @patch('app.services.user_service.UserRepository')
    def test_update_user_not_found(self, mock_repo_class, db_session: Session):
        """존재하지 않는 사용자 업데이트 테스트"""
        mock_repo = Mock()
        mock_repo.update.return_value = None
        mock_repo_class.return_value = mock_repo

        service = UserService(db_session)
        result = service.update_user(999, {"full_name": "New Name"})

        assert result is None
        mock_repo.update.assert_called_once_with(999, {"full_name": "New Name"})